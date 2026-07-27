const padNumber = (value: number) => String(value).padStart(2, '0')

export const parseLocalDate = (value: string) => new Date(value.replace(' ', 'T'))

export const formatDateParam = (date: Date) => {
  return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())}`
}

export const formatMonthParam = (date: Date) => {
  return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}`
}

export const formatDateTimePayload = (timestamp: number) => {
  const date = new Date(timestamp)
  return `${formatDateParam(date)}T${padNumber(date.getHours())}:${padNumber(date.getMinutes())}:00`
}

export const formatDateTimeText = (value: string | number) => {
  const date = typeof value === 'number' ? new Date(value) : parseLocalDate(value)
  return `${date.getMonth() + 1}月${date.getDate()}日 ${padNumber(date.getHours())}:${padNumber(date.getMinutes())}`
}

export const formatTimeText = (value: string) => {
  const date = parseLocalDate(value)
  return `${padNumber(date.getHours())}:${padNumber(date.getMinutes())}`
}

export const formatPeriodText = (value: string) => {
  const hour = parseLocalDate(value).getHours()
  if (hour < 6)
    return '凌晨'
  if (hour < 12)
    return '上午'
  if (hour < 18)
    return '下午'
  return '晚上'
}
