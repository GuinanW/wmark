#!/bin/bash

#find ../_out/ -iname '*.pdf' | while read f;do 
#    nf="${f//./}.pdf"
#    nf="${nf//\//_}"
#    ln "${f}" "${nf}"
#done

pushd ../_out/
for us in *;do
    [ -d "$us" ] || continue
    ln "$us"/*.pdf "../_pdf/${us}.pdf"
done
popd
