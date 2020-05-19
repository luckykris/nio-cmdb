<template>
  <div class="app-container">
    <div class="filter-container">
      <ResourceDefinedSelect
        ref="rsSelect"
        v-model="type"
        index="name"
        style="width: 200px;"
        class="filter-item"
        @change="handleFilter"
      />
      <el-input v-model="listQuery.search" placeholder="Search" clearable class="filter-item" style="width: 130px" />
      <el-select v-model="listQuery.ordering" style="width: 140px" class="filter-item" @change="handleFilter">
        <el-option v-for="item in sortOptions" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        Search
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">
        Add
      </el-button>
      <el-button v-waves :loading="downloadLoading" class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">
        Export
      </el-button>
      <el-checkbox v-model="showReviewer" class="filter-item" style="margin-left:15px;" @change="tableKey=tableKey+1">
        reviewer
      </el-checkbox>
    </div>

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
      @sort-change="sortChange"
    >
      <el-table-column label="ID" prop="id" sortable="custom" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="资源名称" prop="name" />
      <el-table-column label="创建时间" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row._ctime | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="修改时间" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row._mtime | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>
      <template v-for="column in resourceColumns">
        <el-table-column
          v-if="column.resourcetype === ForeignKeyAttributeDefined"
          :key="column.id"
          :label="column.name"
        >
          <template slot-scope="scope">
            <el-tag>{{ scope.row[column.name] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-else-if="column.resourcetype === Many2ManyAttributeDefined"
          :key="column.id"
          :label="column.name"
        >
          <template slot-scope="scope">
            <el-tag
              v-for="v in scope.row[column.name]"
              :key="v"
            >
              {{ v }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-else
          :key="column.id"
          :label="column.name"
        >
          <template slot-scope="scope">
            <span>{{ scope.row[column.name] }}</span>
          </template>
        </el-table-column>
      </template>
      <el-table-column label="Labels" width="150px" align="center">
        <template slot-scope="scope">
          <el-tag
            v-for="t in scope.row.labels"
            :key="t.k"
            size="mini"
            effect="Plain"
            :color="randomTagColor(t.k)"
          >
            <font color="white">{{ t.k }}: {{ t.v }}</font>
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="230" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button disabled type="primary" size="mini" @click="handleUpdate(row)">
            Edit
          </el-button>
          <el-button v-if="row.status!='deleted'" disabled size="mini" type="danger" @click="handleModifyStatus(row,'deleted')">
            Delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="Date" prop="timestamp">
          <el-date-picker v-model="temp.timestamp" type="datetime" placeholder="Please pick a date" />
        </el-form-item>
        <el-form-item label="Title" prop="title">
          <el-input v-model="temp.title" />
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="temp.status" class="filter-item" placeholder="Please select">
            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="Remark">
          <el-input v-model="temp.remark" :autosize="{ minRows: 2, maxRows: 4}" type="textarea" placeholder="Please input" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Cancel
        </el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">
          Confirm
        </el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogPvVisible" title="Reading statistics">
      <el-table :data="pvData" border fit highlight-current-row style="width: 100%">
        <el-table-column prop="key" label="Channel" />
        <el-table-column prop="pv" label="Pv" />
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogPvVisible = false">Confirm</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getResource } from '@/api/resource'
import waves from '@/directive/waves' // waves directive
import { parseTime, randomColor16 } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import ResourceDefinedSelect from '@/views/cmdb/resourceDefined/resourceDefinedSelect'

const calendarTypeOptions = [
  { key: 'CN', display_name: 'China' },
  { key: 'US', display_name: 'USA' },
  { key: 'JP', display_name: 'Japan' },
  { key: 'EU', display_name: 'Eurozone' }
]

const SimpleResourceAttributes = [
  'StringAttributeDefined',
  'IntegerAttributeDefined'
]

const ForeignKeyAttributeDefined = 'ForeignKeyAttributeDefined'
const Many2ManyAttributeDefined = 'Many2ManyAttributeDefined'
// arr to obj, such as { CN : "China", US : "USA" }
const calendarTypeKeyValue = calendarTypeOptions.reduce((acc, cur) => {
  acc[cur.key] = cur.display_name
  return acc
}, {})

export default {
  name: 'ResourceDefinedTable',
  components: { Pagination, ResourceDefinedSelect },
  directives: { waves },
  filters: {
    statusFilter(status) {
      const statusMap = {
        published: 'success',
        draft: 'info',
        deleted: 'danger'
      }
      return statusMap[status]
    },
    typeFilter(type) {
      return calendarTypeKeyValue[type]
    }
  },
  data() {
    return {
      randomTagColorMap: {},
      resourceColumns: [],
      tableKey: 0,
      list: null,
      total: 0,
      type: null,
      listLoading: false,
      listQuery: {
        page: 1,
        limit: 20,
        search: '',
        ordering: '-_ctime'
      },
      importanceOptions: [1, 2, 3],
      calendarTypeOptions,
      ForeignKeyAttributeDefined,
      Many2ManyAttributeDefined,
      SimpleResourceAttributes,
      sortOptions: [
        { label: 'Name Ascending', key: '+name' },
        { label: 'Name Descending', key: '-name' },
        { label: 'Ctime Ascending', key: '+_ctime' },
        { label: 'Ctime Descending', key: '-_ctime' },
        { label: 'Mtime Ascending', key: '+_mtime' },
        { label: 'Mtime Descending', key: '-_mtime' }
      ],
      statusOptions: ['published', 'draft', 'deleted'],
      showReviewer: false,
      temp: {
        id: undefined,
        importance: 1,
        remark: '',
        timestamp: new Date(),
        title: '',
        type: '',
        status: 'published'
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      dialogPvVisible: false,
      pvData: [],
      rules: {
        type: [{ required: true, message: 'type is required', trigger: 'change' }],
        timestamp: [{ type: 'date', required: true, message: 'timestamp is required', trigger: 'change' }],
        title: [{ required: true, message: 'title is required', trigger: 'blur' }]
      },
      downloadLoading: false
    }
  },
  created() {
    // this.getList()
  },
  methods: {
    randomTagColor(k) {
      if (this.randomTagColorMap[k] === undefined) {
        this.randomTagColorMap[k] = randomColor16()
      }
      return this.randomTagColorMap[k]
    },
    getList() {
      this.listLoading = true
      this.resourceColumns = []
      getResource(this.type, this.listQuery).then(response => {
        this.list = response.items
        this.total = response.total
        const rso = this.$refs.rsSelect.getObject()
        this.resourceColumns = rso.attributes
        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleModifyStatus(row, status) {
      this.$message({
        message: '操作Success',
        type: 'success'
      })
      row.status = status
    },
    sortChange(data) {
      const { prop, order } = data
      if (prop === 'id') {
        this.sortByID(order)
      }
    },
    sortByID(order) {
      if (order === 'ascending') {
        this.listQuery.ordering = '+_ctime'
      } else {
        this.listQuery.ordering = '-_ctime'
      }
      this.handleFilter()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        importance: 1,
        remark: '',
        timestamp: new Date(),
        title: '',
        status: 'published',
        type: ''
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          console.log('create')
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.temp.timestamp = new Date(this.temp.timestamp)
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          console.log('update')
        }
      })
    },
    handleDelete(row) {
      this.$notify({
        title: 'Success',
        message: 'Delete Successfully',
        type: 'success',
        duration: 2000
      })
      const index = this.list.indexOf(row)
      this.list.splice(index, 1)
    },
    handleDownload() {
      this.downloadLoading = true
      import('@/vendor/Export2Excel').then(excel => {
        const tHeader = ['timestamp', 'title', 'type', 'importance', 'status']
        const filterVal = ['timestamp', 'title', 'type', 'importance', 'status']
        const data = this.formatJson(filterVal, this.list)
        excel.export_json_to_excel({
          header: tHeader,
          data,
          filename: 'table-list'
        })
        this.downloadLoading = false
      })
    },
    formatJson(filterVal, jsonData) {
      return jsonData.map(v => filterVal.map(j => {
        if (j === 'timestamp') {
          return parseTime(v[j])
        } else {
          return v[j]
        }
      }))
    }
  }
}
</script>
