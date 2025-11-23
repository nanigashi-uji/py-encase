#!/bin/sh
#
# Shell script to make chunk for 'run_py_encase.sh'
#
this="${BASH_SOURCE:-$0}"

src="${this%/*}/../../src/py_encase/py_encase.py"

offset=""
indent="    "
subcmds="$("${PYTHON:-python3}" "${src}" --manage |\
           "${SED:-sed}" -nE -e '/{.*}/ { s/^[[:space:]]*\{(.*)\}[[:space:]]*$/\1/g ; s/, */ /g; p ;}')"

echo "######################################################################"
echo "${offset}"'case "$1" in'
echo "${offset}${indent}$(echo ${subcmds} | sed -e 's/ /|/g' -e 's/$/\)/g')"
echo "${offset}${indent}${indent}if [ -z \"\${proj_name}\" ] ; then"
echo "${offset}${indent}${indent}${indent}echo_usage"
echo "${offset}${indent}${indent}${indent}echo 'Error : Project name is not specified'"
echo "${offset}${indent}${indent}${indent}exit 1"
echo "${offset}${indent}${indent}fi"
echo "${offset}${indent}${indent}py_sbcmd==\"\$1\""
echo "${offset}${indent}${indent}break"
echo "${offset}${indent}${indent};;"
echo "${offset}${indent}*)"
echo "${offset}${indent}${indent}if [ -z \"\${proj_name}\" ] ; then"
echo "${offset}${indent}${indent}${indent}proj_name=\"\$1\""
echo "${offset}${indent}${indent}${indent}shift"
echo "${offset}${indent}${indent}fi"
echo "${offset}${indent}${indent}[ \$# -gt 0 ] && sbcmd==\"\$1\""
echo "${offset}${indent}${indent}break"
echo "${offset}${indent}${indent};;"
echo "${offset}esac"
echo "${offset}[ -z \"\${proj_name}\" ] && { echo_usage ; echo 'Project name is not specified' ; exit 1 ; }"
echo "######################################################################"

sed_exp=$(cat <<EOF 
/^(.* *,)?[[:space:]]+--([^[:space:]]+) ([^[:space:]]+)\$/ {
  s/^(.* *,)?[[:space:]]+--([^[:space:]]+) ([^[:space:]]+)\$/\2/ ;
    /^(help|dry-run|force-install)$/ t
    ;
    h ; s/-/_/g ; x ; H ; x ;
    s/(.*)\n(.*)/\${\1:+ --\2=}\${\1}/g ; p ; x ; t
} ;

/^(.* *,)?[[:space:]]+--([^[:space:]]+) ([^[:space:]]+)[[:space:]]+.*\$/ {
  s/(^.* *,)?[[:space:]]+--([^[:space:]]+) ([^[:space:]]+)[[:space:]]+.*\$/\2/ ;
    /^(help|dry-run|force-install)$/ t
    ;
    h ; s/-/_/g ; x ; H ; x ;
    s/(.*)\n(.*)/\${\1:+ --\2=}\${top_\1}/g ; p ; x ; t
} ;

/^(.* *,)?[[:space:]]+--([^[:space:]]+)[[:space:]]+.*\$/ {
  s/^(.* *,)?[[:space:]]+--([^[:space:]]+)[[:space:]]+.*\$/\2/ ;
    /^(help|dry-run|force-install)$/ t
    ;
    h ; s/-/_/g ; x ; H ; x ;
    s/(.*)\n(.*)/\${\1:+ --\2}/g ; p ; x ; t
} ;

/^(.* *,)?[[:space:]]+--([^[:space:]]+)\$/ {
  s/^(.* *,)?[[:space:]]+--([^[:space:]]+)\$/\2/ ;
    /^(help|dry-run|force-install)$/ t
    ;
    h ; s/-/_/g ; x ; H ; x ;
    s/(.*)\n(.*)/\${\1:+ --\2}/g ; p ; x ; t
} ;


EOF
)

sed_exp_vars=$(cat <<EOF 
/^(.* *,)?[[:space:]]+--([^[:space:]]+) ([^[:space:]]+)\$/ {
  s/^(.* *,)?[[:space:]]+--([^[:space:]]+) ([^[:space:]]+)\$/\2/ ;
    /^(help|dry-run|force-install)$/ t
    ;
    s/-/_/g ; p ; x ; t
} ;

/^(.* *,)?[[:space:]]+--([^[:space:]]+) ([^[:space:]]+)[[:space:]]+.*\$/ {
  s/^(.* *,)?[[:space:]]+--([^[:space:]]+) ([^[:space:]]+)[[:space:]]+.*\$/\2/ ;
    /^(help|dry-run|force-install)$/ t
    ;
    s/-/_/g ; p ; x ; t
} ;

/^(.* *,)?[[:space:]]+--([^[:space:]]+)[[:space:]]+.*\$/ {
  s/^(.* *,)?[[:space:]]+--([^[:space:]]+)[[:space:]]+.*\$/\2/ ;
    /^(help|dry-run|force-install)$/ t
    ;
    s/-/_/g ; p ; x ; t
} ;

/^(.* *,)?[[:space:]]+--([^[:space:]]+)\$/ {
  s/^(.* *,)?[[:space:]]+--([^[:space:]]+)\$/\2/ ;
    /^(help|dry-run|force-install)$/ t
    ;
    s/-/_/g ; p ; x ; t
} ;


EOF
)

subcmds_noopt=""
echo "######################################################################"
echo "${offset}"'case "${py_sbcmd}" in'
for sbcmd in ${subcmds} ; do
    sbcmd_opts="$("${PYTHON:-python3}" "${src}" --manage "${sbcmd}" --help |\
                  "${SED:-sed}" -nE -e "${sed_exp}")"
    [ -z "${sbcmd_opts}" ] && { subcmds_noopt="${subcmds_noopt}${subcmds_noopt:+|}${sbcmd}" ; continue ; }
    echo "${offset}${indent}${sbcmd})"
    echo "${sbcmd_opts}" | "${SED:-sed}" -E -e 's/^(.*)$/'"${offset}${indent}${indent}"'def_opts="\${def_opts}\1"/g'
    echo "${offset}${indent}${indent}break"
    echo "${offset}${indent}${indent};;"
done
if [ -n "${subcmds_noopt}" ]; then
    echo "${offset}${indent}${subcmds_noopt})"
    echo "${offset}${indent}${indent}break"
    echo "${offset}${indent}${indent};;"
    echo "${offset}${indent}-v|--verbose|-h|--help|--manage)"
    echo "${offset}${indent}${indent}continue"
    echo "${offset}${indent}${indent};;"
    echo "${offset}${indent}*)"
    echo "${offset}${indent}${indent};;"
fi
echo "${offset}esac"

buf=$(for sbcmd in ${subcmds} ; do 
          sbcmd_opts="$("${PYTHON:-python3}" "${src}" --manage "${sbcmd}" --help | "${SED:-sed}" -nE -e "${sed_exp_vars}")"
          [ -z "${sbcmd_opts}" ] && { continue ; }
          echo "${sbcmd_opts}" | "${SED:-sed}" -E -e 's/^(.*)$/'"${sbcmd}"' \1/g'
      done)
nline="$(echo "${buf}" | wc -l)"
i=1
vars=''
echo "######################################################################"
echo '###'
echo '### Configuration Parameters'
echo '###'
echo '### For boolian parameter: null-value := False(unset), non-null-value := True(set)'
echo '### '
while [ "$i" -le "${nline}" ]; do
    i=$(expr "$i" + 1)
    line=$(echo "${buf}" | head -$i | tail -1)
    var="$(echo ${line} | cut -d ' ' -f 2)"
    [ -n "$(echo "${vars}" | "${GREP:-grep}" -e "${var}")" ]  &&  continue
    vars="${vars}\n${var}"
    sbcmds=$(echo "${buf}" | "${SED:-sed}" -n -E -e '/ '"${var}"'$/ s/ .*$//gp' | tr '\n' ' ')
#    echo "### ${var} (sub-cmds: ${sbcmds})"
#    echo "# ${var}="
    printf "# %-20s ### %s\n" "${var}=" "(sub-cmds: ${sbcmds})"
done
