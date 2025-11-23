#!/bin/sh
#
# Wrapper shell script to run 'py_encase' with personal default configuration
#
this="${BASH_SOURCE:-$0}"
py_module='py-encase'
py_mod_fn="$(echo "${py_module}" | "${TR:-tr}" '-' '_')"

########################################################################
# Configurable Variables
########################################################################
#
# Specify python & pip if necessary
# 
# PYTHON= 
# PIP=
#
# PY_MOD_VER: "py-encase" to be used (Default = Empty == Latest version)
# PY_MOD_VER=0.0.25

# WORKTOP: Top directory of user working directory
# (Default = Empty == ${HOME}/Documents/workspace )
# WORKTOP="${WORKTOP:-"${HOME}/Documents/workspace"}"

# DEPOT: Location where "py-encase" sub-directory will be created.
# (Default = Empty == ${WORKTOP}/opr/depot
# DEPOT="${DEPOT:-"${HOME}/Documents/workspace/opr/depot"}"

# PY_MOD_DEST: Destination directory of py-encase install.
# (Default = Empty == ${DEPOT}/py-encase-${PY_MOD_VER}
# PY_MOD_DEST = "${PY_MOD_DEST:-"${HOME}/Documents/workspace/opr/depot/py-encase-0.0.24"}"

repo_type_default="local"
def_opts=''

###
### Configuration Parameters
###
### For boolian parameter: null-value := False(unset), non-null-value := True(set)
### 
# prefix=              ### (sub-cmds: init add addlib addkv newmodule )
# prefix="${worktop}/git_workdirs/my_projects/${projname}"
#
# title=               ### (sub-cmds: init newmodule update_readme )
# template=            ### (sub-cmds: init add addlib addkv newmodule update_readme init_git dump_template )
# app_framework=       ### (sub-cmds: init add )
# bare_script=         ### (sub-cmds: init add )
# gui_kvfile=          ### (sub-cmds: init add )
# readme=              ### (sub-cmds: init add addlib )
# required_module=     ### (sub-cmds: init add addlib )
# script_lib=          ### (sub-cmds: init add )
# std_script_lib=      ### (sub-cmds: init add addlib )
# setup_git=           ### (sub-cmds: init )
# git_set_upstream=    ### (sub-cmds: init newmodule init_git )
# git_remote_setup=    ### (sub-cmds: init newmodule init_git )
# git_user_name=       ### (sub-cmds: init newmodule init_git )
# git_user_email=      ### (sub-cmds: init newmodule init_git )
# github_userinfo=     ### (sub-cmds: init newmodule init_git )
# gitlab_userinfo=     ### (sub-cmds: init newmodule init_git )
# git_repository_name= ### (sub-cmds: init newmodule init_git )
# git_hosting=         ### (sub-cmds: init newmodule init_git )
# git_protocol=        ### (sub-cmds: init newmodule init_git )
# git_remote_url=      ### (sub-cmds: init newmodule init_git )
# git_remote_account=  ### (sub-cmds: init newmodule init_git )
# git_remote_host=     ### (sub-cmds: init newmodule init_git )
# git_remote_port=     ### (sub-cmds: init newmodule init_git )
# git_remote_path=     ### (sub-cmds: init newmodule init_git )
# git_remote_sshopts=  ### (sub-cmds: init newmodule init_git )
# git_remote_cmd=      ### (sub-cmds: init newmodule init_git )
# git_remote_share=    ### (sub-cmds: init newmodule init_git )
# git_remote_name=     ### (sub-cmds: init newmodule init_git )
# ssh_command=         ### (sub-cmds: init newmodule init_git )
# gh_command=          ### (sub-cmds: init newmodule init_git )
# glab_command=        ### (sub-cmds: init newmodule init_git )
# move=                ### (sub-cmds: init )
# python=              ### (sub-cmds: init add addlib newmodule )
# git_command=         ### (sub-cmds: init add addlib newmodule init_git )
# verbose=             ### (sub-cmds: info contents init add addlib addkv
#                      ###            newmodule update_readme init_git
#                      ###            dump_template clean distclean selfupdate )
# description=         ### (sub-cmds: newmodule )
# module_website=      ### (sub-cmds: newmodule )
# class_name=          ### (sub-cmds: newmodule )
# keywords=            ### (sub-cmds: newmodule )
# classifiers=         ### (sub-cmds: newmodule )
# author_name=         ### (sub-cmds: newmodule )
# author_email=        ### (sub-cmds: newmodule )
# maintainer_name=     ### (sub-cmds: newmodule )
# maintainer_email=    ### (sub-cmds: newmodule )
# create_year=         ### (sub-cmds: newmodule )
# no_readme=           ### (sub-cmds: newmodule )
# no_git_file=         ### (sub-cmds: newmodule )
# set_shebang=         ### (sub-cmds: newmodule )
# module_src=          ### (sub-cmds: init_git )
# backup=              ### (sub-cmds: update_readme )
# output=              ### (sub-cmds: dump_template )
# long=                ### (sub-cmds: info )
# short=               ### (sub-cmds: info )
# version=             ### (sub-cmds: info )
# pip_module_name=     ### (sub-cmds: info )
# manage_script_name=  ### (sub-cmds: info )
# manage_option=       ### (sub-cmds: info )
# all=                 ### (sub-cmds: contents )
# bin_script=          ### (sub-cmds: contents )
# lib_script=          ### (sub-cmds: contents )
# modules_src=         ### (sub-cmds: contents )

#
# Set variables for each repository type bellow
#

repo_type_select () {
    status=0
    repo_type="$1"
    projname="$2"
    case "${repo_type}" in
        local)
            git_account="${USER}"
            prefix="${worktop}/git_workdirs/${repo_type}/${git_account}/${projname}"
            readme=1
            setup_git=1
            ;;
        selfhosted)
            git_account="${USER}"
            #git_remote_host='git_repo.server.xx.yy'
            prefix="${worktop}/git_workdirs/${git_remote_host:-${repo_type:-selfhosted}}/${git_account}/${projname}"
            readme=1
            setup_git=1
            #git_set_upstream=1
            #git_remote_setup=1
            #git_remote_host='git_repo.server.xx.yy'
            #git_remote_path='/home/..../git_repositories/'
            #git_remote_port=
            #git_user_name=
            #git_user_email="${USER}@${git_remote_host}"
            #git_protocol=ssh
            #git_remote_url=
            #git_remote_account=
            #github_userinfo=1
            #gitlab_userinfo=1
            ;;
        github)
            # github_account='xxxxxxxxxx'
            # github_id='nnnnnnnnnn'
            GHO="$(env NO_COLOR=1 TERM=dumb "${GH:-gh}" api user \
                   --jq '.login,.id' 2>/dev/null)" || exec echo 'GH error'
            eval "$(echo "${GHO}" | "${SED:-sed}" -e '{1 s/^ */github_account=/   ; 2 s/^ */github_id=/   ; s/$//g ; }')"
            github_user_email="${github_id}+${github_account}@users.noreply.github.com"
            prefix="${worktop}/git_workdirs/github/${github_account}/${projname}"
            readme=1
            setup_git=1
            git_set_upstream=1
            git_remote_setup=1
            git_hosting='github'
            github_userinfo=1
            #git_user_name="${github_account}"
            #git_user_email="${github_user_email}"
            #git_remote_account="${github_account}"
            ;;
        gitlab)
            # gitlab_account='xxxxxxxxxx'
            # gitlab_id='nnnnnnnnnn'
            GLO="$(env NO_COLOR=1 TERM=dumb "${GH:-glab}" api user 2> /dev/null |\
                   "${JQ:-jq}" -r '.username,.id')" || exec echo 'GLab error'
            eval "$(echo "${GLO}" | "${SED:-sed}" -e '{1 s/^ */gitlab_account=/ ; 2 s/^ */gitlab_id=/ ; s/$//g ; }')"
            glab_user_email="${gitlab_id}-${gitlab_account}@users.noreply.gitlab.com"

            prefix="${worktop}/git_workdirs/gitlab/${gitlab_account}/${projname}"
            readme=1
            setup_git=1
            git_set_upstream=1
            git_remote_setup=1
            git_hosting='gitlab'
            gitlab_userinfo=1
            #git_user_name="${gitlab_account}"
            #git_user_email="${gitlab_user_email}"
            #git_remote_account="${gitlab_account}"
            ;;
        *)
            repo_type='unknown'
            status=1
            ;;
    esac
    return "${status}"
}


########################################################################
# Local Variables
########################################################################

pip_cmd="${PIP3:-${PIP:-pip3}}"
python_cmd="${PYTHON3:-${PYTHON:-python3}}"
py_mod_version="${PY_MOD_VER-$("${pip_cmd}" index versions "${py_module}" 2>/dev/null |\
                              "${SED:-sed}" -ne '1 {s/^\([^[:space:]]\{1,\}\)[[:space:]]*(\([[:digit:]\.]\{1,\}\)).*$/\2/pg;}' 2>/dev/null)}" 
                                                     
py_mod_spath="${py_module}${py_mod_version:+-}${py_mod_version}"

worktop="${WORKTOP:-${HOME}/Documents/workspace}"
depot="${DEPOT:-${worktop}/opr/depot}"
dest_py_mod="${PY_MOD_DEST:-${depot}/${py_mod_spath}}"
py_encase_runner="${dest_py_mod}/bin/${py_mod_fn}"

########################################################################

echo_usage () {
    echo "[Usage] ${this##*/} [-t repo_type ] [-H] project_name       [${py_module}_options ... ]"
    echo "[Usage] ${this##*/} [-t repo_type ] [-p project_name ] [-H] [${py_module}_options ... ]"
    echo "[Options]"
    echo "         -P proj_name : Repository name"
    echo "         -t repo_type : Repository type (Default: ${repo_type_default})"
    echo "         -n           : Dry-run mode for this script"
    echo "         -v           : Verbose message from this script"
    echo "         -V           : Verbose message"
    echo "         -H           : Show help message (this message)"
    echo "[Available Repository Type options]"
    repo_type_list="$("${SED:-sed}" -n \
                      -e '/^repo_type_select \{1,\}( *) *{/,/^}/ {/^ *case/,/^ *esac/ {/^ [^(]*) *$/ { s/|/ /g; s/[)] *$//g; s/^ \{1,\}//p; } ; } ; }' \
                                   "${this}" |\
                          "${SED:-sed}" -n -e '/^ *\* *$/! p')"

    for x in ${repo_type_list}; do
        echo "        ${x}"
    done
}

# Analyze command line options
OPT=""
OPTARG=""
OPTIND=""
repo_type="${repo_type_default}"
s_dry_run=0
s_verbose=0
proj_name=
while getopts "P:t:nvVH" OPT ; do
    case "${OPT}" in
        P) proj_name="${OPTARG}"
           ;;
        t) repo_type="${OPTARG}"
           ;;
        n) s_dry_run=1
           ;;
        v) s_verbose=1
           ;;
        V) s_verbose=1
           verbose=1
           ;;
        H) echo_usage
           exit 0
           ;;
        \?) echo_usage
           exit 1
           ;;
    esac
done
shift $((OPTIND - 1))
[ $# -gt 0 ] || { echo_usage ; exit 1 ; }
py_sbcmd=''
case "$1" in
    info|contents|init|add|addlib|addkv|newmodule|update_readme|init_git|dump_template|clean|distclean|selfupdate|install|download|freeze|inspect|list|cache|piphelp)
        if [ -z "${proj_name}" ] ; then
            echo_usage
            echo 'Error : Project name is not specified'
            exit 1
        fi
        py_sbcmd="$1"
        break
        ;;
    *)
        if [ -z "${proj_name}" ] ; then
            proj_name="$1"
            shift
        fi
        [ $# -gt 0 ] && { py_sbcmd="$1" ; shift ; }
        break
        ;;
esac
[ -z "${proj_name}" ] && { echo_usage ; echo 'Project name is not specified' ; exit 1 ; }

repo_type_select "${repo_type}" "${proj_name}" || exec echo "Unknown repository type : ${repo_type}"

if [ -f "${py_encase_runner}" ]; then
    :
else
    if [ ${s_dry_run:-0} -ne 0 -o ${s_verbose:-0} -ne 0 ] ; then
        echo mkdir -p "${dest_py_mod}"
        echo "${pip_cmd}" install --upgrade --target "${dest_py_mod}" "${py_module}" || exec echo "Can not install : ${py_module}"
        # --force-reinstall
    fi
    if [ ${s_dry_run:-0} -eq 0  ] ; then
        mkdir -p "${dest_py_mod}"
        "${pip_cmd}" install --upgrade --target "${dest_py_mod}" "${py_module}" || exec echo "Can not install : ${py_module}"
        # --force-reinstall
    fi
fi

if [ "x_${py_sbcmd}" = 'x_init' ]; then
#     py_mod_mngopt="$(env PYTHONPATH="${dest_py_mod}:${PYTHONPATH}" \
#                     "${py_encase_runner}" --manage info --manage-option |\
#                     "${SED:-sed}" -e 's/^[^:]*:[[:space:]]*//g')"
    py_mod_mngopt="--manage"
    flg_no_env=0
elif [ -x "${prefix}/bin/mng_encase" ]; then
    py_encase_runner="${prefix}/bin/mng_encase"
    py_mod_mngopt=""
    flg_no_env=1
elif [ -x "${prefix}/bin/${py_mod_fn}.py" ]; then
    py_encase_runner="${prefix}/bin/${py_mod_fn}.py"
    py_mod_mngopt="--manage"
    flg_no_env=1
fi

if [ ${s_dry_run:-0} -eq 0  ] ; then
    [ -x "${py_encase_runner}" ] || exec echo "Can not execute : ${py_encase_runner}"
fi

case "${py_sbcmd}" in
    info)
        def_opts="${def_opts}${verbose:+ --verbose}"
        def_opts="${def_opts}${long:+ --long}"
        def_opts="${def_opts}${short:+ --short}"
        def_opts="${def_opts}${version:+ --version}"
        def_opts="${def_opts}${pip_module_name:+ --pip-module-name}"
        def_opts="${def_opts}${manage_script_name:+ --manage-script-name}"
        def_opts="${def_opts}${manage_option:+ --manage-option}"
        break
        ;;
    contents)
        def_opts="${def_opts}${verbose:+ --verbose}"
        def_opts="${def_opts}${all:+ --all}"
        def_opts="${def_opts}${bin_script:+ --bin-script}"
        def_opts="${def_opts}${lib_script:+ --lib-script}"
        def_opts="${def_opts}${modules_src:+ --modules-src}"
        break
        ;;
    init)
        def_opts="${def_opts}${prefix:+ --prefix }${prefix}"
        def_opts="${def_opts}${title:+ --title }${title}"
        def_opts="${def_opts}${template:+ --template }${template}"
        def_opts="${def_opts}${app_framework:+ --app-framework}"
        def_opts="${def_opts}${bare_script:+ --bare-script}"
        def_opts="${def_opts}${gui_kvfile:+ --gui-kvfile }${gui_kvfile}"
        def_opts="${def_opts}${readme:+ --readme}"
        def_opts="${def_opts}${module:+ --module }${module}"
        def_opts="${def_opts}${required_module:+ --required-module}"
        def_opts="${def_opts}${script_lib:+ --script-lib }${script_lib}"
        def_opts="${def_opts}${std_script_lib:+ --std-script-lib}"
        def_opts="${def_opts}${setup_git:+ --setup-git}"
        def_opts="${def_opts}${git_set_upstream:+ --git-set-upstream}"
        def_opts="${def_opts}${git_remote_setup:+ --git-remote-setup}"
        def_opts="${def_opts}${git_user_name:+ --git-user-name }${git_user_name}"
        def_opts="${def_opts}${git_user_email:+ --git-user-email }${git_user_email}"
        def_opts="${def_opts}${github_userinfo:+ --github-userinfo}"
        def_opts="${def_opts}${gitlab_userinfo:+ --gitlab-userinfo}"
        def_opts="${def_opts}${git_repository_name:+ --git-repository-name }${git_repository_name}"
        def_opts="${def_opts}${git_hosting:+ --git-hosting }${git_hosting}"
        def_opts="${def_opts}${git_protocol:+ --git-protocol }${git_protocol}"
        def_opts="${def_opts}${git_remote_url:+ --git-remote-url }${git_remote_url}"
        def_opts="${def_opts}${git_remote_account:+ --git-remote-account }${git_remote_account}"
        def_opts="${def_opts}${git_remote_host:+ --git-remote-host }${git_remote_host}"
        def_opts="${def_opts}${git_remote_port:+ --git-remote-port }${git_remote_port}"
        def_opts="${def_opts}${git_remote_path:+ --git-remote-path }${git_remote_path}"
        def_opts="${def_opts}${git_remote_sshopts:+ --git-remote-sshopts }${git_remote_sshopts}"
        def_opts="${def_opts}${git_remote_cmd:+ --git-remote-cmd }${git_remote_cmd}"
        def_opts="${def_opts}${git_remote_share:+ --git-remote-share }${git_remote_share}"
        def_opts="${def_opts}${git_remote_name:+ --git-remote-name }${git_remote_name}"
        def_opts="${def_opts}${ssh_command:+ --ssh-command }${ssh_command}"
        def_opts="${def_opts}${gh_command:+ --gh-command }${gh_command}"
        def_opts="${def_opts}${glab_command:+ --glab-command }${glab_command}"
        def_opts="${def_opts}${move:+ --move}"
        def_opts="${def_opts}${python:+ --python }${python}"
        def_opts="${def_opts}${pip:+ --pip }${top_pip}"
        def_opts="${def_opts}${git_command:+ --git-command }${git_command}"
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    add)
        def_opts="${def_opts}${prefix:+ --prefix }${prefix}"
        def_opts="${def_opts}${readme:+ --readme}"
        def_opts="${def_opts}${template:+ --template }${template}"
        def_opts="${def_opts}${app_framework:+ --app-framework}"
        def_opts="${def_opts}${bare_script:+ --bare-script}"
        def_opts="${def_opts}${gui_kvfile:+ --gui-kvfile }${gui_kvfile}"
        def_opts="${def_opts}${module:+ --module }${module}"
        def_opts="${def_opts}${required_module:+ --required-module}"
        def_opts="${def_opts}${script_lib:+ --script-lib }${script_lib}"
        def_opts="${def_opts}${std_script_lib:+ --std-script-lib}"
        def_opts="${def_opts}${python:+ --python }${python}"
        def_opts="${def_opts}${pip:+ --pip }${top_pip}"
        def_opts="${def_opts}${git_command:+ --git-command }${git_command}"
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    addlib)
        def_opts="${def_opts}${prefix:+ --prefix }${prefix}"
        def_opts="${def_opts}${readme:+ --readme}"
        def_opts="${def_opts}${template:+ --template }${template}"
        def_opts="${def_opts}${module:+ --module }${module}"
        def_opts="${def_opts}${required_module:+ --required-module}"
        def_opts="${def_opts}${std_script_lib:+ --std-script-lib}"
        def_opts="${def_opts}${python:+ --python }${python}"
        def_opts="${def_opts}${pip:+ --pip }${top_pip}"
        def_opts="${def_opts}${git_command:+ --git-command }${git_command}"
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    addkv)
        def_opts="${def_opts}${prefix:+ --prefix }${prefix}"
        def_opts="${def_opts}${template:+ --template }${template}"
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    newmodule)
        def_opts="${def_opts}${prefix:+ --prefix }${prefix}"
        def_opts="${def_opts}${title:+ --title }${title}"
        def_opts="${def_opts}${description:+ --description }${description}"
        def_opts="${def_opts}${template:+ --template }${template}"
        def_opts="${def_opts}${module_website:+ --module-website }${module_website}"
        def_opts="${def_opts}${class_name:+ --class-name }${class_name}"
        def_opts="${def_opts}${module:+ --module }${module}"
        def_opts="${def_opts}${keywords:+ --keywords }${keywords}"
        def_opts="${def_opts}${classifiers:+ --classifiers }${classifiers}"
        def_opts="${def_opts}${author_name:+ --author-name }${author_name}"
        def_opts="${def_opts}${author_email:+ --author-email }${author_email}"
        def_opts="${def_opts}${maintainer_name:+ --maintainer-name }${maintainer_name}"
        def_opts="${def_opts}${maintainer_email:+ --maintainer-email }${maintainer_email}"
        def_opts="${def_opts}${create_year:+ --create-year }${create_year}"
        def_opts="${def_opts}${no_readme:+ --no-readme}"
        def_opts="${def_opts}${no_git_file:+ --no-git-file}"
        def_opts="${def_opts}${git_set_upstream:+ --git-set-upstream}"
        def_opts="${def_opts}${git_remote_setup:+ --git-remote-setup}"
        def_opts="${def_opts}${git_user_name:+ --git-user-name }${git_user_name}"
        def_opts="${def_opts}${git_user_email:+ --git-user-email }${git_user_email}"
        def_opts="${def_opts}${github_userinfo:+ --github-userinfo}"
        def_opts="${def_opts}${gitlab_userinfo:+ --gitlab-userinfo}"
        def_opts="${def_opts}${git_repository_name:+ --git-repository-name }${git_repository_name}"
        def_opts="${def_opts}${git_hosting:+ --git-hosting }${git_hosting}"
        def_opts="${def_opts}${git_protocol:+ --git-protocol }${git_protocol}"
        def_opts="${def_opts}${git_remote_url:+ --git-remote-url }${git_remote_url}"
        def_opts="${def_opts}${git_remote_account:+ --git-remote-account }${git_remote_account}"
        def_opts="${def_opts}${git_remote_host:+ --git-remote-host }${git_remote_host}"
        def_opts="${def_opts}${git_remote_port:+ --git-remote-port }${git_remote_port}"
        def_opts="${def_opts}${git_remote_path:+ --git-remote-path }${git_remote_path}"
        def_opts="${def_opts}${git_remote_sshopts:+ --git-remote-sshopts }${git_remote_sshopts}"
        def_opts="${def_opts}${git_remote_cmd:+ --git-remote-cmd }${git_remote_cmd}"
        def_opts="${def_opts}${git_remote_share:+ --git-remote-share }${git_remote_share}"
        def_opts="${def_opts}${git_remote_name:+ --git-remote-name }${git_remote_name}"
        def_opts="${def_opts}${ssh_command:+ --ssh-command }${ssh_command}"
        def_opts="${def_opts}${gh_command:+ --gh-command }${gh_command}"
        def_opts="${def_opts}${glab_command:+ --glab-command }${glab_command}"
        def_opts="${def_opts}${set_shebang:+ --set-shebang}"
        def_opts="${def_opts}${python:+ --python }${python}"
        def_opts="${def_opts}${pip:+ --pip }${top_pip}"
        def_opts="${def_opts}${git_command:+ --git-command }${git_command}"
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    update_readme)
        def_opts="${def_opts}${title:+ --title }${title}"
        def_opts="${def_opts}${template:+ --template }${template}"
        def_opts="${def_opts}${backup:+ --backup}"
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    init_git)
        def_opts="${def_opts}${module_src:+ --module-src }${module_src}"
        def_opts="${def_opts}${git_set_upstream:+ --git-set-upstream}"
        def_opts="${def_opts}${git_remote_setup:+ --git-remote-setup}"
        def_opts="${def_opts}${git_user_name:+ --git-user-name }${git_user_name}"
        def_opts="${def_opts}${git_user_email:+ --git-user-email }${git_user_email}"
        def_opts="${def_opts}${github_userinfo:+ --github-userinfo}"
        def_opts="${def_opts}${gitlab_userinfo:+ --gitlab-userinfo}"
        def_opts="${def_opts}${git_repository_name:+ --git-repository-name }${git_repository_name}"
        def_opts="${def_opts}${git_hosting:+ --git-hosting }${git_hosting}"
        def_opts="${def_opts}${git_protocol:+ --git-protocol }${git_protocol}"
        def_opts="${def_opts}${git_remote_url:+ --git-remote-url }${git_remote_url}"
        def_opts="${def_opts}${git_remote_account:+ --git-remote-account }${git_remote_account}"
        def_opts="${def_opts}${git_remote_host:+ --git-remote-host }${git_remote_host}"
        def_opts="${def_opts}${git_remote_port:+ --git-remote-port }${git_remote_port}"
        def_opts="${def_opts}${git_remote_path:+ --git-remote-path }${git_remote_path}"
        def_opts="${def_opts}${git_remote_sshopts:+ --git-remote-sshopts }${git_remote_sshopts}"
        def_opts="${def_opts}${git_remote_cmd:+ --git-remote-cmd }${git_remote_cmd}"
        def_opts="${def_opts}${git_remote_share:+ --git-remote-share }${git_remote_share}"
        def_opts="${def_opts}${git_remote_name:+ --git-remote-name }${git_remote_name}"
        def_opts="${def_opts}${ssh_command:+ --ssh-command }${ssh_command}"
        def_opts="${def_opts}${gh_command:+ --gh-command }${gh_command}"
        def_opts="${def_opts}${glab_command:+ --glab-command }${glab_command}"
        def_opts="${def_opts}${git_command:+ --git-command }${git_command}"
        def_opts="${def_opts}${template:+ --template }${template}"
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    dump_template)
        def_opts="${def_opts}${output:+ --output }${output}"
        def_opts="${def_opts}${template:+ --template }${template}"
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    clean)
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    distclean)
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    selfupdate)
        def_opts="${def_opts}${verbose:+ --verbose}"
        break
        ;;
    install|download|freeze|inspect|list|cache|piphelp)
        break
        ;;
esac

if [ -z "${py_sbcmd}" -a ${s_verbose:-0} -ne 0 ] ; then
        echo 'No known sub-command of py_encase is specified.'
else
    [ $# -gt 0 ] && { py_sbcmd="$1" ; shift ; }
fi
    
if [ ${s_dry_run:-0} -ne 0 -o ${s_verbose:-0} -ne 0 ] ; then
    if [ "${flg_no_env:-0}" -eq 0 ]; then
        echo env PYTHONPATH="${dest_py_mod}:${PYTHONPATH}" \
             "${py_encase_runner}" ${py_mod_mngopt} ${py_sbcmd} ${def_opts} $@
    else
        echo "${py_encase_runner}" ${py_mod_mngopt} ${py_sbcmd} ${def_opts} $@
    fi
fi
if [ ${s_dry_run:-0} -eq 0  ] ; then
    if [ "${flg_no_env:-0}" -eq 0 ]; then
        env PYTHONPATH="${dest_py_mod}:${PYTHONPATH}" \
            "${py_encase_runner}" ${py_mod_mngopt} ${py_sbcmd} ${def_opts} $@
    else
        "${py_encase_runner}" ${py_mod_mngopt} ${py_sbcmd} ${def_opts} $@
    fi
fi
