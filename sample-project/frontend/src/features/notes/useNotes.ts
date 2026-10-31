import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { noteKeys, notesApi, type SaveNote } from './notes.api'

export function useNotesList(q: string, page: number) {
  return useQuery({
    queryKey: noteKeys.list(q, page),
    queryFn: ({ signal }) => notesApi.list(q, page, signal),
    placeholderData: keepPreviousData,   // keep the old page on screen while the next one loads
  })
}

export function useNote(id: number) {
  return useQuery({
    queryKey: noteKeys.detail(id),
    queryFn: ({ signal }) => notesApi.get(id, signal),
  })
}

export function useSaveNote() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...body }: SaveNote & { id?: number }) =>
      id === undefined ? notesApi.create(body) : notesApi.update(id, body),
    onSuccess: (note) => {
      client.setQueryData(noteKeys.detail(note.id), note)   // the response is already the new truth
      return client.invalidateQueries({ queryKey: noteKeys.lists() })
    },
  })
}

export function useDeleteNote() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: notesApi.remove,
    onSuccess: (_data, id) => {
      client.removeQueries({ queryKey: noteKeys.detail(id) })
      return client.invalidateQueries({ queryKey: noteKeys.lists() })
    },
  })
}
