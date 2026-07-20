import type { DialogOptions, DialogResult } from '@wot-ui/ui/components/wd-dialog/types'
import { defineStore } from 'pinia'

type GlobalDialogOptions = DialogOptions & {
  success?: (res: DialogResult) => void
  fail?: (res: DialogResult) => void
}

interface GlobalDialog {
  dialogOptions: GlobalDialogOptions | null
  currentPage: string
}

function isButtonPropsObject(value: unknown): value is Record<string, any> {
  return value !== null && CommonUtil.isObj(value)
}

function normalizeButtonProps(props: unknown, text?: string) {
  if (props === null) {
    return null
  }

  if (isButtonPropsObject(props)) {
    return {
      ...props,
      ...(text ? { text } : {}),
    }
  }

  if (CommonUtil.isString(props) || text) {
    return {
      text: text || props,
    }
  }

  if (props === undefined) {
    return {}
  }

  return props
}

function withConfirmOptions(option: GlobalDialogOptions): GlobalDialogOptions {
  const next: GlobalDialogOptions = {
    ...option,
    type: 'confirm',
  }

  if (next.showCancelButton === undefined)
    next.showCancelButton = true

  return next
}

function normalizeDialogOptions(option: GlobalDialogOptions): GlobalDialogOptions {
  const next = withConfirmOptions(option)

  next.confirmButtonProps = normalizeButtonProps(next.confirmButtonProps, next.confirmButtonText) as DialogOptions['confirmButtonProps']

  if (next.showCancelButton === false) {
    next.cancelButtonProps = null
  }
  else if (next.showCancelButton === true || next.cancelButtonProps !== undefined || next.cancelButtonText) {
    next.cancelButtonProps = normalizeButtonProps(next.cancelButtonProps, next.cancelButtonText) as DialogOptions['cancelButtonProps']
  }

  return next
}

function normalizeOption(option: GlobalDialogOptions | string): GlobalDialogOptions {
  return normalizeDialogOptions(CommonUtil.isString(option) ? { title: option } : option)
}

export const useGlobalDialog = defineStore('global-Dialog', {
  state: (): GlobalDialog => ({
    dialogOptions: null,
    currentPage: '',
  }),
  actions: {
    confirm(option: GlobalDialogOptions | string) {
      this.currentPage = getCurrentPath()
      this.dialogOptions = normalizeOption(option)
    },
    close() {
      this.dialogOptions = null
      this.currentPage = ''
    },
  },
})
