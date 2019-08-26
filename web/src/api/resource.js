import request from '@/utils/request'

export function getResourceDefined(params) {
  return request({
    url: '/v1/resourceDefined',
    method: 'get',
    params: params
  })
}

export function getResource(type, params) {
  return request({
    url: '/v1/' + type + '/',
    method: 'get',
    params: params
  })
}
