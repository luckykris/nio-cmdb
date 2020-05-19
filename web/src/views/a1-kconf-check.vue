<template>
  <div class="app-container">
    <el-table
      :data="series"
    >
      <el-table-column
        prop="name"
        label="名称"
        width="180"
      />
      <el-table-column
        label="操作"
        width="180"
      >
        <template slot-scope="scope">
          <el-button type="primary" @click="openDlg(scope.row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog
      :title="dlg_mission_name"
      :visible.sync="dialogVisible"
      width="80%"
    >
      <el-button @click="openCreateDlg">新增</el-button>
      <el-table
        :data="dlg_series"
      >
        <el-table-column
          prop="name"
          label="key"
          width="180"
        />
        <el-table-column
          prop="owner"
          label="责任人"
          width="180"
        />
        <el-table-column
          prop="desc"
          label="描述"
          width="180"
        />
        <el-table-column
          prop="real_value"
          label="当前值"
          width="180"
        >
          <template slot-scope="scope">
            <template v-if="scope.row.real_value == null? false : scope.row.real_value.length > 50">
              <el-button @click="()=>{open_real_draw(scope.row)}">查看详情</el-button>
            </template>
            <template v-else>
              {{ scope.row.real_value }}
            </template>
          </template>
        </el-table-column>
        <el-table-column
          prop="expect_value"
          label="期待值"
          width="180"
        >
          <template slot-scope="scope">
            <template v-if="scope.row.expect_value == null? false : scope.row.expect_value.length > 50">
              <el-button @click="()=>{open_expect_draw(scope.row)}">查看详情</el-button>
            </template>
            <template v-else>
              {{ scope.row.expect_value }}
            </template>
          </template>
        </el-table-column>
        <el-table-column
          prop="is_expect"
          label="是否预期"
          width="180"
        >
          <template slot-scope="scope">
            <el-tag v-if="scope.row.is_expect==true" type="success">符合预期</el-tag>
            <el-tag v-else type="danger">不符合预期</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="name"
          label="操作"
          width="180"
        >
          <template slot-scope="scope">
            <el-button @click="openNewKconfTab(scope.row)">跳转kconf</el-button>
            <el-button type="primary" @click="openEditDlg(scope.row)">编辑</el-button>
            <el-button type="danger" @click="deleteKconf(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
      </span>
      <el-dialog
        title="编辑"
        :visible.sync="dialogEditVisible"
        width="50%"
        append-to-body
      >
        <el-form ref="form" :model="form" label-width="80px">
          <el-form-item label="key">
            <el-input v-model="form.name" />
          </el-form-item>
          <el-form-item label="责任人">
            <el-input v-model="form.owner" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="form.desc" type="textarea" />
          </el-form-item>
          <el-form-item label="期待值">
            <el-input v-model="form.expect_value" type="textarea" />
          </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
          <el-button @click="dialogEditVisible = false">取 消</el-button>
          <el-button v-if="dlg2method=='update'" type="primary" @click="updateKconf">确 定</el-button>
          <el-button v-else-if="dlg2method=='create'" type="primary" @click="createKconf">确 定</el-button>
        </span>
      </el-dialog>
    </el-dialog>
    <el-dialog
      width="60%"
      :title="'真实值'+real_draw_name"
      direction="ltr"
      :visible.sync="real_draw"
    >
      <span>{{ real_draw_value }}</span>
    </el-dialog>
    <el-dialog
      width="60%"
      :title="'期待值'+expect_draw_name"
      :visible.sync="expect_draw"
    >
      <span>{{ expect_draw_value }}</span>
    </el-dialog>
  </div>
</template>

<script>
import waves from '@/directive/waves' // waves directive
import { getMission, getMissionDetail, updateKconfMission, deleteKconfMission, createKconfMission } from '@/api/ext_api'

export default {
  name: 'ResourceDefinedTable',
  directives: { waves },
  data() {
    return {
      series: [],
      dlg_series: [],
      dialogVisible: false,
      dialogEditVisible: false,
      dlg_mission_id: null,
      dlg_mission_name: null,
      form: {},
      dlg2method: 'create',
      real_draw_name: '',
      expect_draw_name: '',
      real_draw_value: '',
      expect_draw_value: '',
      real_draw: false,
      expect_draw: false
    }
  },
  created() {
    this.getList()
  },
  methods: {
    open_expect_draw(row) {
      this.expect_draw_name = row.name
      this.expect_draw_value = row.expect_value
      this.expect_draw = true
    },
    open_real_draw(row) {
      this.real_draw_name = row.name
      this.real_draw_value = row.real_value
      this.real_draw = true
    },
    getList() {
      getMission().then(
        res => {
          this.series = res.items
        }
      ).catch(
        e => {
          console.log(e)
        }
      )
    },
    getKconfList() {
      getMissionDetail({ mission: this.dlg_mission_name })
        .then(
          res => {
            this.dlg_series = res
            console.log(this.dlg_series)
          }
        ).catch(
          e => {
            console.log(e)
          }
        )
    },
    openNewKconfTab(row) {
      const n = row.name
      const regex = /\./gi
      const uri = n.replace(regex, '/')
      window.open('https://kconf.corp.kuaishou.com/#/' + uri)
    },
    openDlg(row) {
      this.dlg_mission_name = row.name
      this.dlg_mission_id = row.id
      this.dialogVisible = true
      this.getKconfList()
    },
    openEditDlg(row) {
      this.dlg2method = 'update'
      this.form = row
      this.dialogEditVisible = true
    },
    openCreateDlg() {
      this.dlg2method = 'create'
      this.form = { kconf_missions: this.dlg_mission_id }
      this.dialogEditVisible = true
    },
    updateKconf() {
      updateKconfMission(this.form)
        .then(
          resp => {
            this.getKconfList()
            this.dialogEditVisible = false
          }
        ).catch(
          e => {
            this.$message('error', e)
          }
        )
    },
    createKconf() {
      createKconfMission(this.form)
        .then(
          resp => {
            this.getKconfList()
            this.dialogEditVisible = false
          }
        ).catch(
          e => {
            this.$message('error', e)
          }
        )
    },
    deleteKconf(row) {
      this.$confirm('此操作将删除该, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteKconfMission(row)
          .then(
            resp => {
              this.getKconfList()
              this.$message({
                type: 'success',
                message: '删除成功!'
              })
            }
          ).catch(
            e => {
              this.$message({
                type: 'error',
                message: e
              })
            }
          )
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    }
  }
}
</script>
