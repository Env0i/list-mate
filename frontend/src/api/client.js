import axios from 'axios'

const client = axios.create({ baseURL: '/api' })

export default client

export const worksApi = {
  list(params) { return client.get('/works', { params }) },
  get(id) { return client.get(`/works/${id}`) },
  create(data) { return client.post('/works', data) },
  update(id, data) { return client.put(`/works/${id}`, data) },
  delete(id) { return client.delete(`/works/${id}`) },
  coverUrl(id) { return `/api/works/${id}/cover` },
}

export const gameProfilesApi = {
  create(workId, data) { return client.post(`/works/${workId}/game-profiles`, data) },
  get(id) { return client.get(`/game-profiles/${id}`) },
  update(id, data) { return client.put(`/game-profiles/${id}`, data) },
  delete(id) { return client.delete(`/game-profiles/${id}`) },
}

export const bangumiApi = {
  search(q, type) { return client.get('/bangumi/search', { params: { q, type } }) },
  get(id) { return client.get(`/bangumi/${id}`) },
}

export const tagsApi = {
  list() { return client.get('/tags') },
  create(data) { return client.post('/tags', data) },
  update(id, data) { return client.put(`/tags/${id}`, data) },
  delete(id) { return client.delete(`/tags/${id}`) },
}

export const statsApi = {
  get() { return client.get('/stats') },
}

export const timelineApi = {
  list(params) { return client.get('/timeline', { params }) },
}

export const attachmentsApi = {
  list(gpid) { return client.get(`/game-profiles/${gpid}/attachments`) },
  upload(gpid, file, label) {
    const fd = new FormData()
    fd.append('file', file)
    if (label) fd.append('label', label)
    return client.post(`/game-profiles/${gpid}/attachments`, fd)
  },
  downloadUrl(id) { return `/api/attachments/${id}` },
  delete(id) { return client.delete(`/attachments/${id}`) },
}

export const exportApi = {
  jsonUrl() { return '/api/export/json' },
  csvUrl() { return '/api/export/csv' },
  backupUrl() { return '/api/backup' },
  restore(formData) { return client.post('/restore', formData) },
}

export const coverApi = {
  upload(id, file) {
    const fd = new FormData()
    fd.append('file', file)
    return client.post(`/works/${id}/cover`, fd)
  },
}
