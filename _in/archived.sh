#!/bin/bash

out_dir=`pwd`'/../_archived/'
mkdir -p "${out_dir}"

pushd "../_out"
pwd

find -type f -exec touch '{}' + 
find -type f -exec md5sum '{}' + > md5sums

for us_dir in *;do
    [ -d "${us_dir}" ] || continue
    password_file="../_generate/${us_dir}/archive.pass"
    #echo "../_generate/${us_dir}/archive.pass"
    [ -f  "${password_file}" ] || continue
    pass=`cat "${password_file}"`

    ls -1 "../${out_dir}/${us_dir}_*.rar" > /dev/null && continue
    name="${us_dir}_"`pwgen 8 1`

    pushd "${us_dir}"
        echo $pass "${out_dir}/${name}.rar"
        rar a -hp"${pass}" -r "${out_dir}/${name}.rar" .
    popd
done
popd
