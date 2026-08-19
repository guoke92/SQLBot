/** Single import-document locator used by pickers, drag-drop and multipart upload. */

const PACKAGE_DOCUMENT = /\.(ya?ml|jsonl?|zip)$/i
const locators = new WeakMap<File, string>()

type FileSystemEntryLike = {
  name: string
  isFile: boolean
  isDirectory: boolean
  file?: (success: (file: File) => void, fail: (error: DOMException) => void) => void
  createReader?: () => {
    readEntries: (success: (entries: FileSystemEntryLike[]) => void) => void
  }
}

export function packageDocumentLocator(file: File): string {
  return (
    locators.get(file) ||
    normalizeLocator(file.webkitRelativePath) ||
    normalizeLocator(file.name)
  )
}

export function collectPackageDocuments(files: Iterable<File>): File[] {
  const collected: File[] = []
  for (const file of files) {
    const locator = packageDocumentLocator(file)
    if (!locator || isIgnoredLocator(locator) || !PACKAGE_DOCUMENT.test(locator)) continue
    locators.set(file, locator)
    collected.push(file)
  }
  return collected
}

export function documentsFromFileList(list: FileList | File[] | null | undefined): File[] {
  return collectPackageDocuments(Array.from(list || []))
}

export async function documentsFromDataTransfer(
  transfer: DataTransfer | null | undefined
): Promise<File[]> {
  const items = Array.from(transfer?.items || [])
  const entries = items
    .map((item) => item.webkitGetAsEntry?.() as FileSystemEntryLike | null | undefined)
    .filter((entry): entry is FileSystemEntryLike => Boolean(entry))
  if (entries.length) {
    return collectPackageDocuments(
      (await Promise.all(entries.map((entry) => readEntry(entry)))).flat()
    )
  }
  return documentsFromFileList(transfer?.files)
}

export function packageSelectionLabel(files: File[]): string {
  if (!files.length) return '尚未选择'
  const locatorsForFiles = files.map(packageDocumentLocator)
  const roots = new Set(
    locatorsForFiles.map((locator) => locator.split('/')[0]).filter(Boolean)
  )
  if (roots.size === 1 && locatorsForFiles.some((locator) => locator.includes('/'))) {
    return `已选择 ${[...roots][0]} · ${files.length} 个文件`
  }
  return `已选择 ${files.length} 个文件`
}

export function packageUploadForm(files: File[]): FormData {
  const form = new FormData()
  files.forEach((file) => form.append('files', file, packageDocumentLocator(file)))
  return form
}

function normalizeLocator(value: string | undefined): string {
  return (value || '')
    .replace(/\\/g, '/')
    .replace(/^\.\/+/, '')
    .replace(/^\/+/, '')
    .split('/')
    .filter((part) => part && part !== '.')
    .join('/')
}

function isIgnoredLocator(locator: string): boolean {
  return locator.split('/').some((part) => part.startsWith('.') || part === '__MACOSX')
}

async function readEntry(entry: FileSystemEntryLike, prefix = ''): Promise<File[]> {
  const relative = prefix ? `${prefix}/${entry.name}` : entry.name
  if (entry.isFile && entry.file) {
    const file = await new Promise<File>((resolve, reject) => entry.file?.(resolve, reject))
    locators.set(file, normalizeLocator(relative))
    return [file]
  }
  if (!entry.isDirectory || !entry.createReader) return []
  const reader = entry.createReader()
  const children: FileSystemEntryLike[] = []
  while (true) {
    const batch = await new Promise<FileSystemEntryLike[]>((resolve) =>
      reader.readEntries(resolve)
    )
    if (!batch.length) break
    children.push(...batch)
  }
  return (await Promise.all(children.map((child) => readEntry(child, relative)))).flat()
}
