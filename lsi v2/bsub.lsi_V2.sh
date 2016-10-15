#!/bin/ksh

# ========================================================================================================================
#
#  File Name      : bsub.application
#
#  Author         : GFI  - subcontracted by AIRBUS
#
#  Platform       : Unix / Linux
#
#  Version:
#       2.0     2015/10/30 JFA - Script version 2 finished and tested
#       1.17    2015/02/06 PCE - Change queue name to [mc_all_x] for all environments
#       1.16    2015/02/06 PCE - Change queue name to [mc_all_x] for production
#       1.15    2015/01/14 PCE - Limit environment ident to the first three characters (dev|int|val|pro)
#       1.14    2014/11/19 PCE - Ignore module CPU estimation, always 1 core asked
#                              - Enhance tracability, use script version in LOG and no more script size
#       1.13    2014/11/10 PCE - Add project LSF estimation functions use
#                              - Add dynamic WENVIRONMENT initial value (Based on get_prodstatus)
#       1.12    2014/10/09 PCE - Wait output file for 300 seconds
#       1.11    2014/10/08 PCE - Remove any kill action and add job output log take back
#       1.10    2014/10/03 PCE - Remove [lsf_tail] function, no more real-time output ascending
#                              - launch [bsub] in synchronous mode
#       1.9     2014/09/30 PCE - [jobs] workaround by using [pstree]
#                              - New function [CleanMyEnvironment] which kill any children and any zombie of current user
#                              - [lsf_tail] is now prent aware
#                              - increase memory to 2Gb
#       1.8     2014/09/16 PCE - Rise [project] parameter to command line and automate [bexec.lsi] directory path value
#       1.7     2014/09/08 PCE - BASH mode
#       1.6     2014/08/27 PCE - Fusion & validation with SVN sources, harmonization versioning
#       1.4     2014/08/14 OKA - wenvironment, new cli parameter
#                                          - WENVIRONMENT: include in INIFILE
#                                          - correct JOB ID monitoring
#                                          - FAIRSHARE_GROUP -> empty for prod
#       1.3     2014/08/05 OKA - update passing parameters between bsub and bexec
#                                                update BEXEC_DIRECTORY, FAISHARE_GROUP, QUEUE for val
#       1.0     2014/06/05 PCE - Script finished and tested
#
#  $Header: @(#) bsub.application   v1.0  2014/06/05 fdb.tfite.hpc@gfi.fr $
#
#  Description    : Script to submit and execute a batch-job(s) via LSF for application
#
# ========================================================================================================================

WDIR=$(cd "$(dirname "$0")";pwd)
WVER="2.0"

# --- Identity & platform specifics

APPLICATION_NAME="lsi"                                                                  # LSI application name
LSF_PROFILE="lsi"                                                                       # LSI LSF profile name
LSI_BINARIES_HOME="/opt/soft/cdtng/tools/lsi"                                           # LSI application home

WENVIRONMENT=$(get_prodstatus | awk -F_ '{print substr($3,1,3)}')                       # Possible values : dev[el] / int / val / pro[d]
[[ ${#WENVIRONMENT} -lt 3 ]] && WENVIRONMENT=int

BEXEC_DIRECTORY=${WDIR}                                                                 # BEXEC directory is the same than current script

# --- To support non-interactive BSUB/BEXEC call because we always need user environment for LSI

[[ -f /etc/profile     ]] && source /etc/profile
[[ -f ${HOME}/.profile ]] && source ${HOME}/.profile
[[ -f ${HOME}/.kshrc   ]] && source ${HOME}/.kshrc

PATH=${PATH}:${WDIR}
export PATH

# ------------------------------------------------------------------------------------------------------------------------
# -- Functions
# ------------------------------------------------------------------------------------------------------------------------

export WLOGCONSTANT="$(hostname)  ${USER}  $(basename "$0")  ${WVER}"
export BSUB_DATE=$(date +%Y%m%d%H%M%S)

# -- Bsub log location variable

BSUBLOGLOCATION=${LSI_DATABANK}/log/${BSUB_DATE}_${USER}_bsub_${LSI_MODULE}.log

# --- LOG one line

Log()
{
        echo "$(date +%Y%m%d%H%M%S)  ${WLOGCONSTANT}  $*"
        [[ ${#LSI_DATABANK} -gt 0 && ${#LSI_MODULE} -gt 0 ]] && echo "$(date +%Y%m%d%H%M%S)  ${WLOGCONSTANT}  $*" >> ${BSUBLOGLOCATION}
}

# --- LOG Info

LogInfo()
{
        Log "INF  $*"
}

# --- LOG Error

LogError()
{
        Log "ERR  $*"
}

# --- LOG each command output

LogCMD()
{
        while read LINE
        do
                if [[ ${LINE} = [0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]* ]]
                then
                        echo "${LINE}"
                else
                        Log "OUT  ${LINE}"
                fi
        done
}

# --- LOG Separator

LogSeparator()
{
        Log "---  ------------------------------------------------------------------------------------------------------------------------"
}

# --- LOG Title

LogTitle()
{
        LogSeparator
        Log "---  $*"
        LogSeparator
}

# --- End on error

EndOnError()
{
        CR=$1
        shift
        LogError "$*"
        CleanMyEnvironment
        [[ ${#JOB_ID} -gt 0 ]] && bkill ${JOB_ID} 2>&1 | LogCMD
        [[ ${#INIFILE} -gt 0 ]] && rm -f ${INIFILE} 2>&1 | LogCMD
        sync
        exit ${CR}
}

# --- Clean the environment before exiting

CleanMyEnvironment()
{
        # Let upper process parent catch all the STDOUT (SEE Station can loose lines without)

        sleep 5
}

# --- Test parameters

need_parameter()
{
        WV=$(eval echo "$"$1)
        [[ -z ${WV} ]] && EndOnError 51 "Parameter [$1] must be set."
}

need_dir()
{
        need_parameter $1
        [[ ! -d $1 ]] && EndOnError 52 "Directory [$1] not found."
}

need_file()
{
        need_parameter $1
        [[ ! -f $1 ]] && EndOnError 53 "File [$1] not found."
}

# --- Help

help_syntax()
{
        echo "--------------------------------------------------------------"
        echo "Syntax : $0 --indir=LSI_DATABANK [Options]"
        echo "---------------------------------------------------------"
        echo ""
        echo "Mandatory parameters :"
        echo ""
        echo " --lsi_module='LSI_MODULE'          : LSI module name"
        echo " --lsi_version='LSI_VERSION'        : LSI module version"
        echo " --lsi_options='LSI_OPTIONS'        : LSI module script call parameters"
        echo " --lsi_output='LSI_OUTPUT'          : List of output files to upload"
        echo " --lsi_databank='LSI_DATABANK'      : Path to pocess DATABANK on peoject filer"
        echo " --project='PROJECT_NAME'           : LSF Project information"
        echo " --bsub_log_file_location='BSUBLOGLOCATION'          : BSUB log file location"
        echo " --bexec_log_file_location='BEXECLOGOCATION'          : BEXEC log file location"
        echo " --post_exec_cmd=POSTEXECCMD        : to be executed after the module launch"
        echo ""
        echo "Options :"
        echo ""
        echo " --wenvironment=xxx                 : Overide environment code              Default : ${WENVIRONMENT}"
        echo " --JOB_NAME=JOB_NAME                : Job name                              Default : ${JOB_NAME}"
        echo " --cpus=NCPUS                       : Number of processors                  Default : ${LSF_REQ_CPU}"
        echo " --mem=LSF_REQ_MEMORY                 : Memory per slot in MB                 Default : ${LSF_REQ_MEMORY}"
        echo " --scratch=LOCAL_SCRATCH_SIZE       : Scratch disk size in MB               Default : ${LSF_REQ_SCRATCH}"
        echo " --temp_local=LOCAL_TEMP_SIZE       : Local Temporary space size in MB      Default : ${TEMP_LOCAL}"
        echo " --temp_global=GLOBAL_TEMP_SIZE     : Global Temporary space size in MB     Default : ${TEMP_GLOBAL}"
        echo " --queue=QUEUE                      : LSF Queue                             Default : ${QUEUE}"
        echo " --lsf_profile='LSF_PROFILE'        : LSF profile to target                 Default : ${LSF_PROFILE}"
        echo " --lsf_resreq='LSF_REQ_EXTRA_RESSOURCES'          : LSF extra ressource requirements      Default : ${LSF_REQ_EXTRA_RESSOURCES}"
        echo " --fairshare_group=GROUP_NAME       : Fairshare group                       Default : ${FAIRSHARE_GROUP}"
        echo " --memory_limit=MEM_LIMIT           : wall limit in memory in MB            Default : If no value given not used"
        echo " --estimated_runtime=ETIME          : wall limit in minutes                 Default : If no value given not used"
        echo " --pre_exec_cmd=PREEXECCMD          : to be executed just before the module launch      Default : If no value given not used"
        echo " --extralsf=EXTRALSF                : additional input argument             Default : If no value given not used"
        echo " --[no]submit                       : Launch or not the job immediately     Default : submit"
        echo " --help                             : Print this help"
        echo ""
        echo "Not operative options:"
        echo ""
        echo "------------------------------------------------------------------------------"
        exit 1
}

# --- Call usage

[[ -z "$1" || "$1" = "--help" || "$1" = "-help" || "$1" = "-h" ]] && help_syntax

# --- TRAP kill

trap 'EndOnError 0 "Killed !" ' HUP INT TERM KILL

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "Reading command line arguments and parameters initialization"
# ------------------------------------------------------------------------------------------------------------------------

# -- Default values

QUEUE=""
FAIRSHARE_GROUP=""
JOB_ID=""

LSF_REQ_CPU="4"
LSF_REQ_MEMORY="2000"
LSF_REQ_SCRATCH="2000"
LSF_REQ_EXTRA_RESSOURCES=""

TEMP_GLOBAL="0"
TEMP_LOCAL="0"
LAUNCH_LSF_JOB="yes"
TRANSFER="yes"
JOB_NAME=""
MEM_LIMIT=""
ETIME=""
PREEXECCMD=""
EXTRALSF=""
BEXECLOGOCATION=""

LSI_MODULE=""
LSI_VERSION=""
LSI_OPTIONS=""
LSI_OUTPUT=""
LSI_DATABANK=""
POSTEXECCMD=""

# -- Parse command line

while [ $# -gt 0 ]
do
        PAR=$1
        shift
        case $PAR in
                --queue=*)
                        QUEUE=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ -z ${QUEUE} ]] && EndOnError 54 "--queue=undefined .... exiting."
                        ;;

                --cpus=*)
                        LSF_REQ_CPU=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ ! -z "${LSF_REQ_CPU##*[!0-9]*}" ]] && EndOnError 54 "Options --cpus=${LSF_REQ_CPU} not an INTEGER ... exiting."
                        ;;

                --mem=*)
                        LSF_REQ_MEMORY=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ ! -z "${LSF_REQ_MEMORY##*[!0-9]*}" ]] && EndOnError 54 "Options --mem=${LSF_REQ_MEMORY} not an INTEGER ... exiting."
                        ;;

                --temp_local=*)
                        TEMP_LOCAL=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ ! -z "${TEMP_LOCAL##*[!0-9]*}" ]] && EndOnError 54 "Options --temp_local=${TEMP_LOCAL} not an INTEGER ... exiting."
                        ;;

                --temp_global=*)
                        TEMP_GLOBAL=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ ! -z "${TEMP_GLOBAL##*[!0-9]*}" ]] && EndOnError 54 "Options --temp_global=${TEMP_GLOBAL} not an INTEGER ... exiting."
                        ;;

                --scratch=*)
                        LSF_REQ_SCRATCH=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ ! -z "${LSF_REQ_SCRATCH##*[!0-9]*}" ]] && EndOnError 54 "Options --scratch=${LSF_REQ_SCRATCH} not an INTEGER ... exiting."
                        ;;

                --JOB_NAME=*)
                        JOB_NAME=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ -z ${JOB_NAME} ]] && EndOnError 54 "--JOB_NAME=undefined .... exiting."
                        ;;

                --lsf_resreq=*)
                        LSF_REQ_EXTRA_RESSOURCES=$(echo "${PAR}" | awk -F"lsf_resreq=" '{print $2}')
                        ;;

                --project=*)
                        PROJECT=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ -z ${PROJECT} ]] && EndOnError 54 "--project=undefined .... exiting."
                        ;;

                --bsub_log_file_location=*)
                        TEMPBSUBLOGLOCATION=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ -z ${TEMPBSUBLOGLOCATION} ]] && EndOnError 54 "--bsub_log_file_location=undefined .... exiting."
                        mv $BSUBLOGLOCATION $TEMPBSUBLOGLOCATION
                        BSUBLOGLOCATION=$TEMPBSUBLOGLOCATION
                        ;;

                --bexec_log_file_location=*)
                        BEXECLOGOCATION=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ -z ${BEXECLOGOCATION} ]] && EndOnError 54 "--bexec_log_file_location=undefined .... exiting."
                        ;;

                --wenvironment=*)
                        WENVIRONMENT=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ -z ${WENVIRONMENT} ]] && EndOnError 54 "--wenvironment=undefined .... exiting."
                        ;;

                --fairshare_group=*)
                        FAIRSHARE_GROUP=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ "${FAIRSHARE_GROUP}c" = "c" ]] && EndOnError 54 "--fairshare_group=undefined .... exiting."
                        ;;

                --submit)
                        LAUNCH_LSF_JOB="yes"
                        ;;

                --nosubmit)
                        LAUNCH_LSF_JOB="no"
                        ;;

                --memory_limit=*)
                        MEM_LIMIT=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ ! -z "${MEM_LIMIT##*[!0-9]*}" ]] && EndOnError 54 "Options --memory_limit=${MEM_LIMIT} not an INTEGER ... exiting."
                        ;;

                --estimated_runtime=*)
                        ETIME=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        [[ ! -z "${ETIME##*[!0-9]*}" ]] && EndOnError 54 "Options --estimated_runtime=${ETIME} not an INTEGER ... exiting."
                        ;;

                --pre_exec_cmd=*)
                        PREEXECCMD=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        ;;

                --extralsf=*)
                        EXTRALSF=$(echo "${PAR}" | awk -F"=" '{print $2}')
                        ;;

                --lsf_profile=*)
                        LSF_PROFILE=$(echo "${PAR}" | awk -F"lsf_profile=" '{print $2}')
                        ;;

                --lsi_module=*)
                        LSI_MODULE=$(echo "${PAR}" | awk -F"lsi_module=" '{print $2}')
                        ;;

                --lsi_version=*)
                        LSI_VERSION=$(echo "${PAR}" | awk -F"lsi_version=" '{print $2}')
                        ;;

                --lsi_options=*)
                        LSI_OPTIONS=$(echo "${PAR}" | awk -F"lsi_options=" '{print $2}')
                        ;;

                --lsi_output=*)
                        LSI_OUTPUT=$(echo "${PAR}" | awk -F"lsi_output=" '{print $2}')
                        ;;

                --lsi_databank=*)
                        LSI_DATABANK=$(echo "${PAR}" | awk -F"lsi_databank=" '{print $2}')
                        ;;

                --post_exec_cmd=*)
                        POSTEXECCMD==$(echo "${PAR}" | awk -F"lsi_databank=" '{print $2}')
                        ;;

                *)
                        EndOnError 55 "Unknown option [${PAR}]"
                        ;;
        esac
done

# -- EXECUTION ENVIRONMENT

need_parameter WENVIRONMENT

case ${WENVIRONMENT} in
        dev*)   [[ ${#FAIRSHARE_GROUP} -lt 1 ]] && FAIRSHARE_GROUP="ug_dev_lsi"
                [[ ${#QUEUE}           -lt 1 ]] && QUEUE="mc_dev_x"
                ;;
        int*)   [[ ${#FAIRSHARE_GROUP} -lt 1 ]] && FAIRSHARE_GROUP="ug_dev_lsi"
                [[ ${#QUEUE}           -lt 1 ]] && QUEUE="mc_dev_x"
                ;;
        val*)   [[ ${#FAIRSHARE_GROUP} -lt 1 ]] && FAIRSHARE_GROUP="ug_val_lsi"
                [[ ${#QUEUE}           -lt 1 ]] && QUEUE="mc_val_x"
                ;;
        pro*)   [[ ${#FAIRSHARE_GROUP} -lt 1 ]] && FAIRSHARE_GROUP=""
                [[ ${#QUEUE}           -lt 1 ]] && QUEUE="mc_all_x"
                ;;
esac

# -- Check parameters

need_parameter PROJECT
need_parameter QUEUE

need_parameter LSI_MODULE
need_parameter LSI_VERSION
need_parameter LSI_OPTIONS
need_parameter LSI_OUTPUT
need_parameter POSTEXECCMD

need_dir "${LSI_DATABANK}"

# -- JOB Variables

WALL_LIMIT=""
[ ! -z ${MEM_LIMIT} ] && WALL_LIMIT="-M \"${MEM_LIMIT}\""
[ ! -z ${ETIME} ] && WALL_LIMIT="${WALL_LIMIT} -We \"${ETIME}\""

[ -z ${JOB_NAME} ] && JOB_NAME=$(echo "${APPLICATION_NAME}_${LSI_MODULE}_$$" | tr '[a-z]' '[A-Z]')
JOB_OUTPUT_FILE="/tmp/LSI-${USER}-$(hostname -s)-${JOB_NAME}.out"

if [ ${TEMP_GLOBAL} -gt 0 ]
then
        JOB_WORKDIR=GLOBAL_TEMP
else
        [ ${LSF_REQ_SCRATCH} -gt 0 ] && JOB_WORKDIR="LOCAL_SCRATCH" || JOB_WORKDIR="LOCAL_TEMP"
fi

# --- Job's LSF ressources estimation

LSF_REQ_CPU="1"

if [[ -f ${LSI_ESTIMATION_SCRIPT_NAME} ]]
then
        source ${LSI_ESTIMATION_SCRIPT_NAME}
        #DISABLED# LSF_REQ_CPU=$(lsi_lsf_estimate_cpu "${LSI_DATABANK}")
        LSF_REQ_MEMORY=$(lsi_lsf_estimate_memory "${LSI_DATABANK}")
        LSF_REQ_SCRATCH=${LSF_REQ_MEMORY}
else
        #DISABLED# LSF_REQ_CPU="4"
        LSF_REQ_MEMORY="2000"
        LSF_REQ_SCRATCH="2000"
fi

#DISABLED# [[ ${LSF_REQ_CPU} != [0-9]* ]] && LogInfo "Bad [LSF_REQ_CPU]" && LSF_REQ_CPU="4"
[[ ${LSF_REQ_MEMORY} != [0-9]* ]] && LogInfo "Bad [LSF_REQ_MEMORY]" && LSF_REQ_MEMORY="2000"
[[ ${LSF_REQ_SCRATCH} != [0-9]* ]] && LogInfo "Bad [LSF_REQ_SCRATCH]" && LSF_REQ_SCRATCH="2000"

# -- Control on queue

if [[ ${LSF_REQ_CPU} -eq 1 ]]
then
        QUEUE=$(echo "${QUEUE%_*}")"_ser"
else
        QUEUE=$(echo "${QUEUE%_*}")"_par"
fi

# -- Temporary space needed

[[ "${JOB_WORKDIR}" = "GLOBAL_TEMP" ]] && LSF_REQ_SCRATCH=${TEMP_GLOBAL}
[[ "${JOB_WORKDIR}" = "LOCAL_TEMP"  ]] && LSF_REQ_SCRATCH=${TEMP_LOCAL}

# -- LSI module execution script

LSI_SCRIPT_NAME=xmllint --xpath '/xxx/xxx/xxx/text()' saga.xml
[[ -z ${LSI_SCRIPT_NAME} ]] && EndOnError 54 "LSI_SCRIPT_NAME=undefined .... exiting."

LSI_ESTIMATION_SCRIPT_NAME="${LSI_BINARIES_HOME}/${LSI_VERSION}/${LSI_MODULE}/lsf.sh"

# -- Module catalogue location

CATALOGLOCATION=xmllint --xpath '/xxx/xxx/xxx/text()' saga.xml
[[ -z ${CATALOGLOCATION} ]] && EndOnError 54 "CATALOGLOCATION=undefined .... exiting."

# -- BEXEC out data

BEXEC_OUT_DATA=xmllint --xpath '/xxx/xxx/xxx/text()' saga.xml | sed 's:</out>:</out>" ":g'

# -- Job script extras

[ ! -z ${LSF_REQ_EXTRA_RESSOURCES} ] && EXTRA_RESOURCE=" -R \"${LSF_REQ_EXTRA_RESSOURCES}\"" || EXTRA_RESOURCE=""
[ ! -z ${FAIRSHARE_GROUP} ] && FAIRSHARE="-G \"${FAIRSHARE_GROUP}\"" || FAIRSHARE=""

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "${APPLICATION_NAME} LAUNCHER"
# ------------------------------------------------------------------------------------------------------------------------

LogInfo "JOBNAME                         : ${JOB_NAME}"
LogInfo "Queue                           : ${QUEUE}"
LogInfo "Nb of processors                : ${LSF_REQ_CPU}"
LogInfo "Memory per slots (in MB)        : ${LSF_REQ_MEMORY}"
LogInfo "Job workdir                     : \${$JOB_WORKDIR} ${GLOBAL_TEMP}"
LogInfo "Disk space needed (in MB)       : ${LSF_REQ_SCRATCH}"
LogInfo "Submission Host                 : $(hostname)"
LogInfo "LSF extra resource requirements : ${LSF_REQ_EXTRA_RESSOURCES}"
LogInfo "Project                         : ${PROJECT}"
LogInfo "Fairshare group                 : ${FAIRSHARE_GROUP}"
LogInfo "JOBFILE                         : ${JOB_OUTPUT_FILE}"
LogInfo "LSF Profile                     : ${LSF_PROFILE}"
LogInfo "Module                          : ${LSI_MODULE}"
LogInfo "Version                         : ${LSI_VERSION}"
LogInfo "Module options                  : ${LSI_OPTIONS}"
LogInfo "Input databank                  : ${LSI_DATABANK}"
LogInfo "Pre execution command           : ${PREEXECCMD}"
LogInfo "Post execution command          : ${POSTEXECCMD}"
LogInfo "Extra LSF                       : ${EXTRALSF}"
LogInfo "Bexec log file location         : ${BEXECLOGOCATION}"

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "Job submission"
# ------------------------------------------------------------------------------------------------------------------------

# --- Create JOB parameters file

INIFILE=$(mktemp /tmp/LSI-${HOSTNAME}-XXXXXX)

cat << EOT > $INIFILE

export WENVIRONMENT=$WENVIRONMENT        # int/dev/val/pro
export LSI_SCRIPT_NAME=$LSI_SCRIPT_NAME  # Module script absolute path
export CATALOGLOCATION=$CATALOGLOCATION  # Module catalog location
export BEXEC_OUT_DATA=$BEXEC_OUT_DATA    # BEXEC out data
export LSI_MODULE=$LSI_MODULE            # Module identity
export TRANSFER=$TRANSFER                # Flag to activate en-job results upload
export JOB_WORKDIR=$JOB_WORKDIR          # Absolute path of execution directory
export LSI_OUTPUT=$LSI_OUTPUT            # Module outputs files comma or blank separated
export LSI_DATABANK=$LSI_DATABANK        # Databank HOME
export LSI_SCRIPT_OPTIONS="$LSI_OPTIONS" # Module script options
export PREEXECCMD=$PREEXECCMD            # Pre execution command
export BEXECLOGOCATION=$BEXECLOGOCATION  # BEXEC log file location

EOT

# --- Launch the JOB in SYNCHRONOUS MODE

BSUB_COMMAND_CALL="bsub -q \"${QUEUE}\" ${EXTRA_RESOURCE} ${WALL_LIMIT} -app ${LSF_PROFILE} -J ${JOB_NAME} -n ${LSF_REQ_CPU} -R \"rusage[mem=${LSF_REQ_ME
MORY},${JOB_WORKDIR}_SIZE=${LSF_REQ_SCRATCH}]\" -P \"${PROJECT}\" ${FAIRSHARE} -f \"${INIFILE} > ${INIFILE}\" --extralsf=${EXTRALSF} -o \"${JOB_OUTPUT_FILE}\" 
-Ep ${POSTEXECCMD} -f \"${JOB_OUTPUT_FILE} < ${JOB_OUTPUT_FILE}\" ${BEXEC_DIRECTORY}/bexec.${APPLICATION_NAME} ${INIFILE}"

LogInfo "BSUB_COMMAND_CALL : ${BSUB_COMMAND_CALL}"
LogInfo "BEXEC directory   : ${BEXEC_DIRECTORY}"
LogInfo "BSUB              : $(which bsub)"

LogInfo "Job submission"
[ "${TRANSFER}" = "yes" ] && LogInfo "Results will be copied in [${LSI_DATABANK}]"
LogInfo "Logs of execution will be copied in [${JOB_OUTPUT_FILE}]"

if [ "${LAUNCH_LSF_JOB}" = "yes" ]
then
        LogInfo "Call LSF"
        JOB_LAUNCH=$(eval ${BSUB_COMMAND_CALL} 2>&1)
        JOB_CR=$?
        [[ ${JOB_CR} -ne 0 ]] && EndOnError 56 "Job error [ERROR=${JOB_CR}]"
else
        LogInfo "No submission, launch job manually with following command :"
        LogInfo "${BSUB_COMMAND_CALL}"
fi

# --- Finish

[[ ${#INIFILE} -gt 0 ]] && rm -f ${INIFILE}

LogSeparator

CleanMyEnvironment
exit 0