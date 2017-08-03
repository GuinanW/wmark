#!/bin/bash

ya_disk_params="-c /mnt/disk3/cloud/yandex-other/cfg/ya-other.cfg" #доп параметры для ya-disk
ya_disk_dir="book/new_book" #каталог, куда выгружены
org_id="111" #id орга

out_hide_file="../user_hides.txt"
echo > "${out_hide_file}"

yandex-disk ${ya_disk_params} start

for f in *.{rar,zip,7z};do
    [ -f "${f}" ] || continue
    user_id="${f%%_*}"
    pass=`cat "../_generate/${user_id}/archive.pass"`

    ret=0
#    7z t -p"${pass}" "${f}" # проверка архива
#    ret=$?
    if [ $ret -ne 0 ];then
        echo "${f}" >> _error
        continue
    fi

    echo "${user_id} ${f} ${pass}"
    yandex_url=`yandex-disk ${ya_disk_params} publish "${ya_disk_dir}/${f}"`

    cat << EOF >> "${out_hide_file}"
[HIDE='user=${org_id},${user_id}']
  ${yandex_url}
  пароль: ${pass}
[/HIDE]

EOF

done

yandex-disk ${ya_disk_params} stop
