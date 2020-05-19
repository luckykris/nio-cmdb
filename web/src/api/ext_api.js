import request from '@/utils/request'

export function getMission(params) {
  return request({
    url: '/v1/mission/',
    method: 'get',
    params: params
  })
}

export function getMissionDetail(params) {
  return request({
    url: '/ext/get-mission',
    method: 'get',
    params: params
  })
}

export function updateKconfMission(data) {
  return request({
    url: 'v1/kconf-mission/' + data.id + '/',
    method: 'put',
    data: data
  })
}

export function deleteKconfMission(data) {
  return request({
    url: '/v1/kconf-mission/' + data.id + '/',
    method: 'delete'
  })
}

export function createKconfMission(data) {
  return request({
    url: '/v1/kconf-mission/',
    method: 'post',
    data: data
  })
}
