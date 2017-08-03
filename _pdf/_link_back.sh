#!/bin/bash

filename="book.pdf"

for f in *.pdf;do
    us="${f%%.pdf}"
    outfile="../_out/${us}/${filename}"
    #[ -f "${outfile}" ] || continue
    num_links=`stat --printf "%h" "${f}"`
    #echo "${f}" "${num_links}"
    if [ $num_links -eq 1 ];then
        mv -v "${f}" "${outfile}"
    fi
done

#find ../_out/ -iname '*.pdf' | while read f;do 
#    nf="${f//./}.pdf"
#    nf="${nf//\//_}"
#    ln "${f}" "${nf}"
#done
