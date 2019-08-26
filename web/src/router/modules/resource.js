/** When your routing table is too long, you can split it into small modules **/

import Layout from '@/layout'

const resourceRouter = {
  path: '/resource',
  component: Layout,
  name: 'Resource',
  meta: {
    title: 'Resource',
    icon: 'table'
  },
  children: [
    {
      path: 'resourceDefinedTable',
      component: () => import('@/views/cmdb/resourceDefined/resourceDefinedTable'),
      name: 'resourceDefinedTable',
      meta: { title: 'Define' }
    },
    {
      path: 'resourceTable',
      component: () => import('@/views/cmdb/resource/resourceTable'),
      name: 'resourceTable',
      meta: { title: 'Items' }
    }
  ]
}
export default resourceRouter
