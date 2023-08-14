interface File {
  id: number
  name: string
}
interface Files {
  [key: number]: File
}

export type {File, Files}
