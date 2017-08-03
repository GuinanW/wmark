#!/bin/bash
#сборка конечного djvu

filename="book.djvu"
#filename="book_gray.djvu"
base_dirname=`pwd`"/.."
out_dir=`pwd`"/../_out"

diff_page=1 #разница нумераций

#cp -vf out.djvu "${out_file}"
tmp_file=`mktemp`
#tmp_dir=`mktemp -d`
tmp_dir="/tmp/_mutagen_djvu/"
tmp_dir_djvu="${tmp_dir}/_extra"

mkdir -p "${tmp_dir}/_split" "${tmp_dir}/_merge"
djvmcvt -i "${filename}" "${tmp_dir}/_split" _ind.djvu

pushd "../_generate"
for us_dir in *;do
    [ -d "${us_dir}" ] || continue
    pushd "${us_dir}"

    #out_file="${base_dirname}/_out/${us_dir}/${filename}"
    out_file="${out_dir}/${us_dir}/${filename}"
    mkdir -p `dirname "${out_file}"`
    mkdir -p "${tmp_dir_djvu}"
    
    rsync -avHP --delete "${tmp_dir}/_split/" "${tmp_dir}/_merge/"

    for pic_file in *.bg44;do
        #pic_file="../_tmp/${f}"
        file_txtz="${tmp_dir_djvu}/tmp.txtz"
        file_fgbz="${tmp_dir_djvu}/tmp.fgbz"
        file_sjbz="${tmp_dir_djvu}/tmp.incl"
        file_incl="${tmp_dir_djvu}/tmp.sjbz"
        file_bg44="${tmp_dir_djvu}/tmp.bg44"
        f="${tmp_dir}/_merge/${pic_file%%.*}.djvu"
        [ -f "${f}" ] || continue
        cmd=""

        echo "${bn}"
        djvuextract "${f}" INCL="${file_incl}" Sjbz="${file_sjbz}" TXTz="${file_txtz}" FGbz="${file_fgbz}"
        cmd="${cmd} INFO=,,600 INCL=`sed  -r 's#\.iff(\w)#.iff INCL=\1#g' ${file_incl}` Sjbz=${file_sjbz}"
        if [ -f "${pic_file}" ];then
            djvuextract "${pic_file}" BG44="${file_bg44}"
            cmd="${cmd} BG44=${file_bg44}"
        fi
        [ -f "${file_fgbz}" ] && cmd="${cmd} FGbz=${file_fgbz}"
        [ -f "${file_txtz}" ] && cmd="${cmd} TXTz=${file_txtz}"
        echo $cmd
        pushd  "${tmp_dir}/_merge/"
        djvumake "${f}" $cmd
        popd
    done

    djvmcvt -b "${tmp_dir}/_merge/_ind.djvu" "${out_file}"
    #cp -vf "../${filename}" "${out_file}"

    #ссылки в тексте и дополнительные элементы, можно сделать в djvusmooth
    for i in `seq -w 0001 2000`;do
        txt_ant="${i}.ant" #ссылки и прочее
        page_num=`expr ${i} + ${diff_page}`
        [ -f "${txt_ant}" ]  && echo "select ${page_num}; set-ant ${txt_ant}" >> "${tmp_file}"
        txt_text="${i}.txt" #текст
        [ -f "${txt_text}" ]  && echo "select ${page_num}; set-txt ${txt_text}" >> "${tmp_file}"
        txt_meta="${i}.meta" #текст
        [ -f "${txt_meta}" ]  && echo "select ${page_num}; set-ant ${txt_meta}" >> "${tmp_file}"
    done 

    cat "${tmp_file}" | djvused -s "${out_file}"

    rm "${tmp_file}"
    popd
done
popd
rm -rf "${tmp_dir}"

# #eeeeee
