<template>
  <el-dialog
    width="90%"
    :visible.sync="dialogVisible"
    :title="title"
  >
    <el-form ref="from2" :model="resourceDefined" label-width="80px">
      <el-form-item label="name">
        <el-input v-model="resourceDefined.name" />
      </el-form-item>
    </el-form>
    <template v-if="method!=='create'">
      <el-dialog
        width="40%"
        :title="innerTitle"
        :visible.sync="innerDialogVisible"
        append-to-body
      >
        <el-form ref="form" :model="form" label-width="80px">
          <el-form-item label="name">
            <el-input v-model="form.name" />
          </el-form-item>
          <el-form-item label="type">
            <el-select
              v-model="form.resourcetype"
              :disabled="innerTitle === textMap.update"
              with="100%"
            >
              <el-option v-for="at in attributeType" :key="at.name" :label="at.name" :value="at.name" />
            </el-select>
            <template v-if="attributeTypeShowRelateList.indexOf(form.resourcetype)> -1">
              <span>Rlate:</span>
              <el-select
                v-model="form.relate"
                :disabled="innerTitle === textMap.update"
              >
                <el-option v-for="at in resourceDefinedList" :key="at.name" :label="at.name" :value="at.id" />
              </el-select>
            </template>
          </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
          <el-button @click="innerDialogVisible = false">Cancel</el-button>
          <el-button v-if="innerTitle === textMap.update" type="primary" @click="updateAttribute">Update</el-button>
          <el-button v-else type="primary" @click="createAttribute">Create</el-button>
        </span>
      </el-dialog>
      <el-button type="primary" @click="openInnerDlg(textMap.create, {})">增加字段</el-button>
      <el-table
        :data="tableData"
        :span-method="arraySpanMethod"
        border
        :loading="loading"
        style="width: 100%"
      >
        <el-table-column
          prop="_ctime"
          label="create time"
          width="180"
        />
        <el-table-column
          prop="_mtime"
          label="create time"
          width="180"
        />
        <el-table-column
          prop="name"
          label="name"
          width="180"
        >
          <template slot-scope="{row}">
            <template v-if="row.edit">
              <el-input v-model="row.name" />
            </template>
            <template v-else>
              <span>{{ row.name }}</span>
            </template>
          </template>
        </el-table-column>
        <el-table-column
          prop="resourcetype"
          label="type"
        />
        <el-table-column
          prop="relate"
          label="relate resource"
        >
          <template slot-scope="{row}">
            {{ resource_map[row.relate] }}
          </template>
        </el-table-column>
        <el-table-column
          prop="default"
          label="default value"
        />
        <el-table-column
          label="action"
        >
          <template slot-scope="{row}">
            <el-button size="mini" type="primary" @click="openInnerDlg(textMap.update,row)">
              编辑
            </el-button>
            <el-button size="mini" type="danger" @click="deleteAttribute(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </template>
    <span slot="footer" class="dialog-footer">
      <el-button type="primary" @click="dialogVisible = false">close</el-button>
      <el-button v-if="method === 'create'" @click="createResourceDefined">create</el-button>
    </span>
  </el-dialog>
</template>

<script>
import { getResourceDefined, putAttributeDefined, postAttributeDefined, postResourceDefined, deleteAttributeDefined } from '@/api/resource'
import { deepClone } from '@/utils'
const empty_form = {
  name: '',
  create_hook: null,
  update_hook: null,
  delete_hook: null,
  attributes: []
}
export default {
  name: 'ResourceDefinedDlg',
  data() {
    return {
      dialogVisible: false,
      innerDialogVisible: false,
      title: 'default title',
      innerTitle: 'default title',
      method: null,
      tableData: [],
      resourceDefined: {},
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      form: {},
      loading: false,
      resource_map: {}
    }
  },
  computed: {
    attributeType() {
      return this.$store.getters['resource'].attributeType
    },
    attributeTypeShowRelateList() {
      return this.$store.getters['resource'].attributeTypeShowRelateList
    },
    resourceDefinedList() {
      return this.$store.getters['resource'].resourceDefinedList
    }
  },
  created() {
  },
  methods: {
    deepClone,
    createResourceDefined() {
      postResourceDefined(this.resourceDefined)
        .then(
          res => {
            this.$emit('reload-event')
            this.dialogVisible = false
          }
        ).catch(
          e => {
            console.log(e)
          }
        )
    },
    updateAttribute() {
      putAttributeDefined(this.form)
        .then(
          res => {
            this.form = res
            this.$emit('reload-event')
            this.innerDialogVisible = false
          }
        ).catch(
          e => {
            console.log(e)
          }
        )
    },
    createAttribute() {
      this.form.resourceDefined = this.resourceDefined.id
      postAttributeDefined(this.form)
        .then(
          res => {
            this.tableData.push(res)
            this.$emit('reload-event')
            this.innerDialogVisible = false
          }
        ).catch(
          e => {
            console.log(e)
          }
        )
    },
    deleteAttribute(row) {
      this.$confirm('确定要删除' + row.name + '字段吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteAttributeDefined(row.id)
          .then(
            res => {
              let ii = null
              for (let i = 0; i < this.tableData.length; i++) {
                if (this.tableData[i].name === row.name) {
                  ii = i
                  break
                }
              }
              if (ii !== null) {
                this.tableData.splice(ii, 1)
              }
              this.$emit('reload-event')
            }
          ).catch(
            e => {
              this.$message.error('删除失败:' + e)
            }
          )
      }).catch(() => {
      })
    },
    openInnerDlg(title, data, method) {
      this.form = deepClone(data)
      this.innerTitle = title
      this.innerDialogVisible = true
    },
    load(id) {
      getResourceDefined()
    },
    openDlg(title, data, method) {
      this.title = title
      this.method = method
      this.dialogVisible = true
      if (method === 'create') {
        this.resourceDefined = JSON.parse(JSON.stringify(empty_form))
        return
      }
      this.resourceDefined = JSON.parse(JSON.stringify(data))
      const kvls = []
      data.attributes.forEach(
        item => {
          if (item.relate !== null) {
            kvls.push(item.id)
          }
        }
      )

      if (kvls.length > 0) {
        this.loading = true
        getResourceDefined({ ids: kvls, limit: 0 })
          .then(
            res => {
              const m = {}
              res.forEach(
                item2 => {
                  m[item2.id] = item2.name
                }
              )
              this.resource_map = m
              this.tableData = data.attributes
              this.loading = false
            }
          )
      } else {
        this.tableData = data.attributes
        this.loading = false
      }
    },
    arraySpanMethod({ row, column, rowIndex, columnIndex }) {
      if (row.relate === undefined) {
        if (columnIndex === 3) {
          return [1, 2]
        } else if (columnIndex === 4) {
          return [1, 0]
        }
      }
    }
  }
}
</script>
