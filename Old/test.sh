#!/bin/bash

WTABCHARBAD=(Æ æ Œ œ À à Á á Â â Ã ã Ä ä È è É é Ê ê Ë ë Ì ì Í í Î î Ï ï Ò ò Ó ó Ô ô Õ õ Ö ö Ù ù Ú ú Û û Ü ü Ý ý Ÿ ÿ Ñ ñ Ç ç € \\)
WTABCHARREP=(AE ae OE oe A a A a A a A a A a E e E e E e E e I i I i I i I i O o O o O o O o O o U u U u U u U u Y y Y y N n C c e _)
WLCHARGOOD='][!#$%()+-.<>=?@_{}~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
WCHARDEFAULT='_'
WLCHARGOODESCAPED=$(echo "${WLCHARGOOD}" | sed -e 's:\\:\\\\:' -e 's:\$:\\$:' -e 's:\.:\\.:' -e 's:\*:\\*:' -e 's:\/:\\/:' -e 's:\^:\\^:' -e 's:\-:\\-:' -e 's:\!:\\!:')

test=bœtchÆgoli^lol\\Ÿ

echo "0 " "$test"

wonn=$test

for char in "${!WTABCHARBAD[@]}"
do
	if [[ "${WTABCHARBAD[$char]}" == "\\" ]]
	then
		WTABCHARBAD[$char]=$(echo ${WTABCHARBAD[$char]} | sed -e 's:\\:\\\\:')
	fi

	if grep -q "${WTABCHARBAD[$char]}" <<< "$test"
	then
		wonn=$(echo "$wonn" | sed "s:${WTABCHARBAD[$char]}:${WTABCHARREP[$char]}:g") 
		echo "1 " "$wonn"
	fi

done

wonn2=$(echo "$wonn" | sed "s:[^${WLCHARGOODESCAPED}]:${WCHARDEFAULT}:g")
echo "2 " "$wonn2"
