#!/bin/bash

git_rev_short=$(git rev-parse --short HEAD)
echo "git rev short is : ${git_rev_short}"
sh archive.sh "${git_rev_short}"
package_path=$(ls dist/dynamic-cmdb-"${git_rev_short}"*)
echo "package path is : ${package_path}"
./upload_product_to_ksp.sh -n dynamic-cmdb -f "${package_path}"
