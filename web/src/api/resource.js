import request from '@/utils/request'

export function getResourceDefined(params) {
  return request({
    url: '/v1/resource-defined',
    method: 'get',
    params: params
  })
}

export function getResourceDefinedObj(id) {
  return request({
    url: '/v1/resource-defined/' + id + '/',
    method: 'get'
  })
}

export function putResourceDefined(params) {
  return request({
    url: '/v1/resource-defined/' + params.id + '/',
    method: 'put',
    data: params
  })
}

export function postResourceDefined(params) {
  return request({
    url: '/v1/resource-defined/',
    method: 'post',
    data: params
  })
}

export function deleteResourceDefined(id) {
  return request({
    url: '/v1/resource-defined/' + id + '/',
    method: 'delete'
  })
}

export function getResource(type, params) {
  return request({
    url: '/v1/' + type + '/',
    method: 'get',
    params: params
  })
}

export function countResource(type) {
  return request({
    url: '/v1/' + type + '/count',
    method: 'get'
  })
}

export function getAttributeType() {
  return request({
    url: '/v1/attribute-types/',
    method: 'get'
  })
}

export function putAttributeDefined(data) {
  return request({
    url: '/v1/attribute-defined/' + data.id + '/',
    method: 'put',
    data: data
  })
}

export function postAttributeDefined(data) {
  return request({
    url: '/v1/attribute-defined/',
    method: 'post',
    data: data
  })
}

export function deleteAttributeDefined(id) {
  return request({
    url: '/v1/attribute-defined/' + id + '/',
    method: 'delete'
  })
}
