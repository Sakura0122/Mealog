const EXIF_MARKER = 0xE1
const EXIF_IFD_POINTER_TAG = 0x8769
const DATE_TIME_TAG = 0x0132
const DATE_TIME_ORIGINAL_TAG = 0x9003
const DATE_TIME_DIGITIZED_TAG = 0x9004

const parseExifDate = (value: string): number | null => {
  const matched = /^(\d{4}):(\d{2}):(\d{2}) (\d{2}):(\d{2}):(\d{2})$/.exec(value)
  if (!matched)
    return null

  const [, yearText, monthText, dayText, hourText, minuteText, secondText] = matched
  const parts = [yearText, monthText, dayText, hourText, minuteText, secondText].map(Number)
  const [year, month, day, hour, minute, second] = parts
  const date = new Date(year, month - 1, day, hour, minute, second)
  if (
    date.getFullYear() !== year
    || date.getMonth() !== month - 1
    || date.getDate() !== day
    || date.getHours() !== hour
    || date.getMinutes() !== minute
    || date.getSeconds() !== second
  ) {
    return null
  }
  return date.getTime()
}

const parseTiffDate = (view: DataView, tiffOffset: number): number | null => {
  if (tiffOffset + 8 > view.byteLength)
    return null

  const byteOrder = view.getUint16(tiffOffset, false)
  const littleEndian = byteOrder === 0x4949
  if (!littleEndian && byteOrder !== 0x4D4D)
    return null
  if (view.getUint16(tiffOffset + 2, littleEndian) !== 42)
    return null

  const readUint16 = (offset: number) => view.getUint16(offset, littleEndian)
  const readUint32 = (offset: number) => view.getUint32(offset, littleEndian)
  const firstIfdOffset = tiffOffset + readUint32(tiffOffset + 4)

  const findEntry = (ifdOffset: number, targetTag: number) => {
    if (ifdOffset + 2 > view.byteLength)
      return null
    const entryCount = readUint16(ifdOffset)
    for (let index = 0; index < entryCount; index += 1) {
      const entryOffset = ifdOffset + 2 + index * 12
      if (entryOffset + 12 > view.byteLength)
        return null
      if (readUint16(entryOffset) === targetTag)
        return entryOffset
    }
    return null
  }

  const readAsciiEntry = (entryOffset: number | null): string | null => {
    if (entryOffset === null || readUint16(entryOffset + 2) !== 2)
      return null
    const length = readUint32(entryOffset + 4)
    const valueOffset = length <= 4 ? entryOffset + 8 : tiffOffset + readUint32(entryOffset + 8)
    if (length === 0 || valueOffset + length > view.byteLength)
      return null

    let value = ''
    for (let index = 0; index < length; index += 1) {
      const character = view.getUint8(valueOffset + index)
      if (character === 0)
        break
      value += String.fromCharCode(character)
    }
    return value
  }

  // 拍摄时间位于 Exif 子 IFD，DateTime 仅作为少数相机缺失标准字段时的兜底。
  const exifPointerEntry = findEntry(firstIfdOffset, EXIF_IFD_POINTER_TAG)
  const exifIfdOffset = exifPointerEntry === null
    ? null
    : tiffOffset + readUint32(exifPointerEntry + 8)
  const dateValue = exifIfdOffset === null
    ? null
    : readAsciiEntry(findEntry(exifIfdOffset, DATE_TIME_ORIGINAL_TAG))
      ?? readAsciiEntry(findEntry(exifIfdOffset, DATE_TIME_DIGITIZED_TAG))
  return parseExifDate(dateValue ?? readAsciiEntry(findEntry(firstIfdOffset, DATE_TIME_TAG)) ?? '')
}

const parseJpegTakenAt = (buffer: ArrayBuffer): number | null => {
  const view = new DataView(buffer)
  if (view.byteLength < 4 || view.getUint16(0, false) !== 0xFFD8)
    return null

  let offset = 2
  while (offset + 4 <= view.byteLength) {
    if (view.getUint8(offset) !== 0xFF)
      return null
    const marker = view.getUint8(offset + 1)
    if (marker === 0xDA || marker === 0xD9)
      break

    const segmentLength = view.getUint16(offset + 2, false)
    if (segmentLength < 2 || offset + 2 + segmentLength > view.byteLength)
      return null
    if (
      marker === EXIF_MARKER
      && segmentLength >= 8
      && view.getUint32(offset + 4, false) === 0x45786966
      && view.getUint16(offset + 8, false) === 0
    ) {
      const takenAt = parseTiffDate(view, offset + 10)
      if (takenAt !== null)
        return takenAt
    }
    offset += 2 + segmentLength
  }
  return null
}

export const getImageTakenAt = async (filePath: string): Promise<number | null> => {
  let buffer: ArrayBuffer | null = null

  // 微信选图接口不返回拍摄时间，只能读取原图中的 EXIF；其他平台保留当前时间。
  // #ifdef MP-WEIXIN
  buffer = await new Promise((resolve) => {
    wx.getFileSystemManager().readFile({
      filePath,
      success: ({ data }) => resolve(data instanceof ArrayBuffer ? data : null),
      fail: () => resolve(null),
    })
  })
  // #endif

  if (!buffer)
    return null
  try {
    return parseJpegTakenAt(buffer)
  }
  catch {
    return null
  }
}
