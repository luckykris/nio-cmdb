#!/bin/sh

# set -x
# 检查python3
# 线上ops把py3.6安装在/usr/local/python3目录中
#PY3_CMD="/usr/bin/python36"
PY3_CMD=`which python3`
if [[ ! -x "${PY3_CMD}" ]]; then
    echo "没有找到python3命令，请联系ops，安装python3"
    exit 1
fi

# 检查py3版本是否大于等于3.6
PY3_VERSION=`${PY3_CMD} -c "import sys; vi=sys.version_info; print(vi[0]*1000+vi[1]*100+vi[2]*10)"`
if [[ "${PY3_VERSION}" -lt 3600 ]]; then
    echo "python3 version is low, please upgrade your python3 at least 3.6"
    exit 1
fi

run_sh_dir=$(cd "$(dirname "$0")"; pwd)



# 运行echo
code_dir=$1
echo "work directory :${code_dir}"


if [[ -f ${run_sh_dir}/ksp_hostvars  ]]; then
    source ${run_sh_dir}/ksp_hostvars  # 激活在ksp上注册的变量，即导入到环境变量中
fi



cd ${code_dir}
${PY3_CMD} -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -Ur requirements.txt
pip install -U infra-kconf -i https://pypi.corp.kuaishou.com/kuaishou/prod/
export PYTHONPATH=${code_dir}
exec python manage.py runserver 0.0.0.0:8000 --settings settings-${ksp_instance_group}
