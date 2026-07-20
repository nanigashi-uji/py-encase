#!/bin/sh
this="${0##*/}"
python_cmd="${PYTHON3:-${PYTHON:-python3}}"
pip_cmd="${PIP3:-${PIP:-pip3}}"

dest_top="${TMPDIR:-/tmp}"
dest_subdir="${USER:-uuuuu}/sandbox-$(printf "%09d" $$)/py-encase"
dest="${dest_top%/}/${dest_subdir%/}"

verbose=0
dryrun=0
keep=0
force=0

echo_help () {
    echo "[Usage]    % ${this} [option] prefix [py-encase arguments]"   1>&2
    echo "[options]"                                                    1>&2
    echo "          -v      :  verbose output"                          1>&2
    echo "          -n      :  dry-run mode"                            1>&2
    echo "          -f      :  force overwrite"                         1>&2
    echo "          -D dir  :  directory where py-encase is installed"  1>&2
    echo "          -k      :  Keep py-encase (Do not clean directory)" 1>&2
    echo "          -h      :  Show this message"                       1>&2
}

while getopts "vnfD:kh" OPT; do
    case "${OPT}" in
        v)  verbose=1 ;;
        n)  dryrun=1 ;;
        f)  force=1 ;;
        k)  keep=1 ;;
        D)  dest="${OPTARG}" ;;
        h)  echo_help ; exit 0 ;;
        \?) echo_help ; exit 1 ;;
    esac
done
shift $((OPTIND-1))

case ${dest} in
    '') echo "[ERROR] -D directory must not be empty" 1>&2 ; exit 1 ;;
    -*) dest="./${dest}" ;;
esac

case "/${dest}/" in
    */../*) echo "[ERROR] -D path must not contain '..': ${dest}" 1>&2 ; exit 1 ;;
esac

if [ $# -lt 1 ]; then
    echo "[ERROR] prefix directory is not specified" 1>&2
    echo_help 
    exit 1 
fi
prefix="$1"
shift

if [ "${verbose:-0}" -ne 0 ]; then
    _flg=0
    for _x in "$@"; do
        if [ "x${_x}" = "x-v" ] || [ "x${_x}" = "x--verbose" ]; then
            _flg=1
            break
        fi    
    done
    if [ ${_flg:-0} -eq 0 ]; then
        set -- "--verbose" "$@"
    fi
fi

if [ -z "${prefix}" ]; then
    echo "[ERROR] prefix directory must not be empty" 1>&2
    exit 1
fi

if [ -e "${prefix}" ] || [ -L "${prefix}" ] ; then
    if [ ${force:-0} -eq 0 ]; then
        echo "[ERROR] prefix directory exists :  ${prefix} : stopped" 1>&2
        exit 1
    else
        echo "[WARNING] prefix directory exists :  ${prefix}  (force overwrite mode)" 1>&2
    fi
fi

to_be_created(){
    fullpath="$1"
    case ${fullpath} in
        /*) upper=/ ; subdirs=${fullpath#/} ;;
        *)  upper=. ; subdirs=${fullpath}   ;;
    esac
    while [ -n "${subdirs}" ]; do
        case "${subdirs}" in
            */*) component="${subdirs%%/*}" ; subdirs="${subdirs#*/}" ;;
            *)   component="${subdirs}"     ; subdirs=                ;;
        esac
        [ -n "${component}" ] || continue
        case ${upper} in
            /) upper="/${component}"       ;;
            *) upper="${upper}/${component}" ;;
        esac
        if [ \! -e "${upper}" ] && [ \! -L "${upper}" ] ; then
            case "${upper}" in
                ./*) printf '%s\n' "${upper#./}" ;;
                *)   printf '%s\n' "${upper}"    ;;
            esac
            return 0
        fi
    done
    return 1
}

top_created="$(to_be_created "${dest}")" || top_created=
top_created_done=0

invoke_cmd () {
    if [ ${verbose:-0} -ne 0 ] || [ ${dryrun:-0} -ne 0 ] ; then
        echo "$@" 1>&2
    fi
    if [ ${dryrun:-0} -eq 0 ]; then
        "$@"
    fi
}

try_rmdir() {
    if [ "${verbose:-0}" -ne 0 ] \
           || [ "${dryrun:-0}" -ne 0 ]; then
        printf '%s\n' "rmdir ${1}" 1>&2
    fi
    if [ "${dryrun:-0}" -eq 0 ]; then
        rmdir "${1}" 2>/dev/null
    fi
}

rm_created_dirs() {
    cleanup_status=0

    if [ -z "${top_created}" ] \
           || [ "${top_created_done:-0}" -eq 0 ] \
           || [ "${keep:-0}" -ne 0 ]; then
        return 0
    fi

    invoke_cmd rm -rf "${dest}" || cleanup_status=$?

    rtop="${top_created%/}"
    rmtgt="${dest%/}"

    [ -n "${rtop}" ]  || rtop='/'
    [ -n "${rmtgt}" ] || rmtgt='/'

    if [ "${rtop}" = "${rmtgt}" ]; then
        return "${cleanup_status}"
    fi

    curdir="$(dirname "${rmtgt}")" || return 1
    while :; do
        case "${curdir}/" in
            "${rtop}/"|"${rtop}/"*)       ;;
            *)                      break ;;
        esac

        try_rmdir "${curdir}" || break

        if [ "x${curdir}" = "x${rtop}" ]; then
            break
        fi

        upprdir="$(dirname "${curdir}")" || { cleanup_status=1 ; break ; }
        if [ "x${upprdir}" = "x${curdir}" ]; then
            break
        fi
        curdir="${upprdir}"
    done
    return "${cleanup_status}"
}


clean_up() {
    signal="${1-}"
    cleanup_status=0
    trap '' HUP INT QUIT PIPE TERM

    rm_created_dirs || cleanup_status=$?
    
    if [ -n "${signal}" ]; then
        trap - "${signal}"
        kill -s "${signal}" "$$"
        exit 1
    fi

    return "${cleanup_status}"
}

if [ ${verbose:-0} -ne 0 ]; then
    echo "dest        = '${dest}'"        1>&2
    echo "top_created = '${top_created}'" 1>&2
    echo "prefix      = '${prefix}'"      1>&2
    echo "options     = '$@'"             1>&2
fi

status=0

try_mkdir() {
    if [ "${verbose:-0}" -ne 0 ] \
           || [ "${dryrun:-0}" -ne 0 ]; then
        printf '%s\n' "mkdir ${1}" 1>&2
    fi
    if [ "${dryrun:-0}" -eq 0 ]; then
        mkdir "${1}" 2>/dev/null
    fi
}


if [ -n "${top_created}" ]; then
    for i in HUP INT QUIT PIPE TERM; do
        trap 'clean_up '"${i}" "${i}"
    done

    invoke_cmd umask 077 || status=$?
    
    while [ "${status}" -eq 0 ] \
              && [ -n "${top_created}" ] \
              && [ "${top_created_done:-0}" -eq 0 ]; do

        mkdir_target="${top_created}"
        if try_mkdir "${mkdir_target}"; then
            top_created="${mkdir_target}"
            top_created_done=1
        elif [ -d "${mkdir_target}" ] \
                 && [ ! -L "${mkdir_target}" ]; then
            top_created="$(to_be_created "${dest}")" || top_created=
            if [ -z "${top_created}" ]; then
                echo "[ERROR] Destination was created concurrently: ${dest}" 1>&2
                status=1
            fi
        else
            echo "[ERROR] Cannot create directory: ${mkdir_target}" 1>&2
            status=1
        fi
    done

    if [ "${status}" -eq 0 ]; then
        invoke_cmd mkdir -p "${dest}"
        mkdir_p_status=$?

        if [ "${mkdir_p_status}" -ne 0 ]; then
            status=${mkdir_p_status}
            echo "[ERROR] Cannot create directory: ${dest}" >&2
        fi
    fi
fi

if [ "${status}" -eq 0 ]; then
    invoke_cmd "${pip_cmd}" install --target "${dest}" py-encase || status=$?
fi

if [ "${status}" -eq 0 ]; then
    invoke_cmd env PYTHONPATH="${dest}" \
               PIP="${pip_cmd}" PIP3="${pip_cmd}" \
               "${python_cmd}" "${dest}/bin/py_encase" \
               "--manage" "init" --prefix="${prefix}" "$@" || status=$?
fi

cleanup_status=0

if [ ${keep:-0} -ne 0 ]; then
    if [ "${dryrun:-0}" -ne 0 ]; then
        echo "Dry-run: working directory would be kept under '${dest}'" >&2
    elif [ "${status}" -eq 0 ]; then
        echo "Installed py-encase is kept under '${dest}'"              >&2
    else
        echo "Incomplete working directory is kept under '${dest}'"     >&2
    fi
else
    clean_up || cleanup_status=$?
fi


if [ "${status}" -eq 0 ]; then
    status=${cleanup_status}
fi

exit "${status}"
