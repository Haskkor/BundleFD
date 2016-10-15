#!/bin/bash

# ========================================================================================================================
#
#  File Name      : bexec.application
#
#  Author         : GFI  - subcontracted by AIRBUS
#
#  Platform       : Unix / Linux
#
#  Version:
#       2.0     2015/10/30 JFA - Script version 2 finished and tested
#       1.16    2015/02/10 PCE - Change [lsrun] to [scp] (Meeting GSA, PCE, DSE, AHU)
#                              - Change message on input SCP when file not found
#       1.15    2015/01/15 PCE - Correct [lsrun] commands
#       1.14    2015/01/14 PCE - Use FULLPATH file names for upload of result files
#       1.13    2014/12/18 PCE - Force RWX access mode on all scratch downloaded files
#       1.12    2014/11/19 PCE - Enhance tracability, use script version in LOG and no more script size
#       1.11    2014/10/14 PCE - Remove [sleep] and [CleanMyEnvironment] too
#       1.10    2014/10/09 PCE - Remove [kill]
#       1.9     2014/10/08 PCE - Remove synchronization wait
#       1.8     2014/09/30 PCE - New function [CleanMyEnvironment] which kill any children of current user
#       1.7     2014/09/08 PCE - BASH mode
#       1.6     2014/08/27 PCE - Fusion & validation with SVN sources
#       1.5     2014/08/19 OKA - update error logging for code error 30
#                                            simplify GLOBAL_TEMP check
#       1.4     2014/08/13 OKA - update WENVIRONNMENT
#       1.3     2014/08/05 OKA - update passing parameters between bsub and bexec
#       1.0     2014/06/05 PCE - Script finished and tested
#
#  $Header: @(#) bsub.application   v1.0  2014/06/05 fdb.tfite.hpc@gfi.fr $
#
#  Description    : Script to submit and execute a batch-job(s) via LSF for application
#
# ========================================================================================================================

WDIR=$(cd "$(dirname "$0")";pwd)
WVER="2.0"

# --- Retrieve parameters

INIFILE=$1
[[ ! -f $INIFILE ]] && echo "Error : problem with transfer of INIFILE $INIFILE" && exit 20
chmod 755 $INIFILE
source $INIFILE
rm -f $INIFILE

# --- To support non-interactive BSUB/BEXEC call because we always need user environment for LSI

[[ -f /etc/profile     ]] && source /etc/profile
[[ -f ${HOME}/.profile ]] && source ${HOME}/.profile
[[ -f ${HOME}/.kshrc   ]] && source ${HOME}/.kshrc

# ------------------------------------------------------------------------------------------------------------------------
# -- EXECUTION ENVIRONMENT
# ------------------------------------------------------------------------------------------------------------------------

LSI_FILER_HOME_REGEX="/projects/A350_LSI/run/.*/.*/data/"

# ------------------------------------------------------------------------------------------------------------------------
# -- Functions
# ------------------------------------------------------------------------------------------------------------------------

export WLOGCONSTANT="$(hostname)  ${USER}  $(basename "$0")  ${WVER}"
export BEXEC_DATE=$(date +%Y%m%d%H%M%S)

# --- LOG one line

Log()
{
        echo "$(date +%Y%m%d%H%M%S)  ${WLOGCONSTANT}  $*"
        [[ ${#LOCALDB} -gt 0 ]] && echo "$(date +%Y%m%d%H%M%S)  ${WLOGCONSTANT} $*" >> ${BSUBLOGLOCATION}/${BEXEC_DATE}_${USER}_bexec_${LSI_MODULE}.log
}

# --- LOG Info

LogInfo()
{
        Log "INF  $*"
}

# --- LOG Error

LogError()
{
        Log "BEXEC_ERROR_CODE=$*"
}

# --- LOG each command output

LogCMD()
{
        while read LINE
        do
                if [[ ${LINE} = [0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]* ]]
                then
                        echo "${LINE}"
                        [[ ${#LOCALDB} -gt 0 ]] && echo "${LINE}" >> ${LOCALDB}/log/${BEXEC_DATE}_${USER}_bexec_${LSI_MODULE}.log
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
        sync
        exit ${CR}
}

# --- LOG upload

LogUpload()
{
        cd "${LOCALDB}"
        for file in $(ls */[0-9]*.log */*/[0-9]*.log 2>/dev/null)
        do
                LogInfo "Upload [${file}]"
                set -o pipefail
                scp "${LOCALDB}/${file}" "${LSB_SUB_HOST}:${LSI_DATABANK}/log/." 2>&1 | LogCMD
                CR=$?
                if [[ ${CR} -ne 0 ]]
                then
                        LogInfo "Transfer error [${CR}]."
                        ls -ld  ${LOCALDB}/${file} 2>&1 | LogCMD
                        #[[ ! -z ${GLOBAL_TEMP} ]] && LogInfo "Moving files to ${GLOBAL_TEMP}" && mv * ${GLOBAL_TEMP}
                        #LogError "Transfer of output files with errors !!!!"
                fi
        done
}

# --- TRAP kill

trap 'EndOnError 0 "Killed !" ' HUP INT TERM KILL

# --- LSF stdout & stderr trapping desynchronization workaround

export BEXEC_DATE=$(date +%Y%m%d%H%M%S)

export LOCALDB=$(eval echo \$${JOB_WORKDIR})
LogInfo "Create/Validate [${LOCALDB}]."
set -o pipefail
mkdir -p ${LOCALDB}/{data,log,tmp} 2>&1 | LogCMD
[[ $? -ne 0 ]] && EndOnError 21 "Cannot create/valdiate [${LOCALDB}] elements."

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "START [bexec.lsi]"
# ------------------------------------------------------------------------------------------------------------------------

LogInfo "Machine        : $(uname -a)"
LogInfo "LSB_MCPU_HOSTS : ${LSB_MCPU_HOSTS}"

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "Reading command line arguments and parameters initialization"
# ------------------------------------------------------------------------------------------------------------------------

LogInfo "List of arguments of [$0] :"
LogInfo "1 - LSI_SCRIPT_NAME    : ${LSI_SCRIPT_NAME}"
LogInfo "2 - MODULE             : ${LSI_MODULE}"
LogInfo "3 - TRANSFER           : ${TRANSFER}"
LogInfo "4 - JOB_WORKDIR        : ${JOB_WORKDIR}"
LogInfo "5 - LSI_OUTPUT         : ${LSI_OUTPUT}"
LogInfo "6 - LSI_DATABANK       : ${LSI_DATABANK}"
LogInfo "7 - LSI_SCRIPT_OPTIONS : ${LSI_SCRIPT_OPTIONS}"

# ------------------------------------------------------------------------------
------------------------------------------
LogTitle "Variables definitions"
# ------------------------------------------------------------------------------
------------------------------------------

# -- Application special task

LogInfo "Go to [${LOCALDB}]"
cd ${LOCALDB} 1>/dev/null 2>&1
[[ $? -ne 0 ]] && EndOnError 22 "Cannot move to [${LOCALDB}]."

export WFILELIST=$(echo "${LSI_SCRIPT_OPTIONS}" | sed 's/[^ ]*=/ /g' | sed 's/ */\n/g' | sed "s/'//g" | egrep "^${LSI_FILER_HOME_REGEX}")
#export LSI_DATABANK=$(echo "${WFILELIST}" | sed 's!  *!\n!g' | sed 's!/data/.*!!g' | sort -u)
export WDIRSCRATCH=${LOCALDB}

LogInfo "WFILELIST       : $(echo ${WFILELIST} | tr -d '\r')"
LogInfo "LSI_DATABANK       : ${LSI_DATABANK}"
LogInfo "WDIRSCRATCH     : ${WDIRSCRATCH}"

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "Prepare databank structure"
# ------------------------------------------------------------------------------------------------------------------------

mkdir -p ${LOCALDB}/data ${LOCALDB}/log ${LOCALDB}/tmp 2>&1 | LogCMD
[[ $? -ne 0 ]] && EndOnError 23 "Cannot create [${LOCALDB}] structure."

LogInfo "Directory content before download :"
(cd ${LOCALDB};find . -exec ls -ld "{}" ";" 2>&1) | LogCMD

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "Transfer catalog"
# ------------------------------------------------------------------------------------------------------------------------

file=${LSI_DATABANK}/data/lsi.cat
LogInfo "Download [${file}]"
set -o pipefail
scp "${LSB_SUB_HOST}:${file}" "${LOCALDB}/data/." 2>&1 | LogCMD
CR=$?
if [[ ${CR} -ne 0 ]]
then
        LogInfo "Transfer error [${CR}]."
        echo "" > ${LOCALDB}/data/lsi.cat
fi







# ------------------------------------------------------------------------------------------------------------------------
LogTitle "Transfer input files"
# ------------------------------------------------------------------------------------------------------------------------

for file in $(echo ${WFILELIST} | tr -d '\r')
do
        LogInfo "Download [${file}]"
        set -o pipefail
        scp "${LSB_SUB_HOST}:${file}" "${LOCALDB}/data/." 2>&1 | LogCMD
        CR=$?
        if [[ ${CR} -eq 1 ]]
        then
                LogInfo "File not found, perhaps an output."
        elif [[ ${CR} -ne 0 ]]
        then
                LogInfo "Transfer error [${CR}]."
        else
                WFILENAME=$(basename "${file}")
                if [[ $(stat -c%s "${LOCALDB}/data/${WFILENAME}") = 0 ]]
                then
                        LogInfo "Ignore empty input."
                        rm -f "${LOCALDB}/data/${WFILENAME}"
                        LSI_SCRIPT_OPTIONS=$(echo "${LSI_SCRIPT_OPTIONS}" | sed "s!${LSI_DATABANK}/data/${WFILENAME}!!g")
                else
                        chmod u+rwx "${LOCALDB}/data/${WFILENAME}"
                        WREALNAME=$(grep "^ident ${WFILENAME}=" ${LOCALDB}/data/lsi.cat | sed 's!.*=!!' | sed 's!.*/!!')
                        if [[ ${#WREALNAME} -gt 0 && ${WFILENAME} != ${WREALNAME} && ${WREALNAME} != wf-input-* ]]
                        then
                                LogInfo "Renaming to [${WREALNAME}]."
                                LSI_SCRIPT_OPTIONS=$(echo "${LSI_SCRIPT_OPTIONS}" | sed "s!/${WFILENAME}'!/${WREALNAME}'!g")
                                set -o pipefail
                                mv "${LOCALDB}/data/${WFILENAME}" "${LOCALDB}/data/${WREALNAME}" 2>&1 | LogCMD
                                CR=$?
                                [[ ${CR} -ne 0 ]] && EndOnError 30 "Cannot move[${LOCALDB}/data/${WFILENAME} to ${LOCALDB}/data/${WREALNAME}]."
                        fi
                fi
        fi
done

LogInfo "Databank content after download :"
LogInfo "PATH : ${LOCALDB}"
(cd ${LOCALDB};find . -exec ls -ld "{}" ";" 2>&1) | LogCMD









# ------------------------------------------------------------------------------------------------------------------------
LogTitle "Start of pre execution command"
# ------------------------------------------------------------------------------------------------------------------------

if [[ -z ${$PREEXECCMD}]]
then
        LogInfo "Pre execution command is empty"
else
        ${PREEXECCMD} 2>&1 | LogCMD | tee
        RC_EXEC=$?
        if [[ ${RC_EXEC} -ne 0 ]]
        then
                LogUpload
                EndOnError 57 "Execution error on the pre exeecution comand : ${RC_EXEC}"
        fi        

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "Start computation"
# ------------------------------------------------------------------------------------------------------------------------

LSI_SCRIPT_CALL=$(echo "${LSI_SCRIPT_NAME} ${LSI_SCRIPT_OPTIONS}" | sed 's!'${LSI_DATABANK}'!'${WDIRSCRATCH}'!g')
LogInfo "RUN : ${LSI_SCRIPT_CALL}"
set -o pipefail
${LSI_SCRIPT_CALL} 2>&1 | LogCMD | tee
RC_EXEC=$?
if [[ ${RC_EXEC} -ne 0 ]]
then
        LogUpload
        EndOnError 50 "Execution error (see ${JOB_WORKDIR} for debugging) : ${RC_EXEC}"
fi

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "Upload data listed as out in the XML file"
# ------------------------------------------------------------------------------------------------------------------------

LogUpload

if [[ -z "${BEXEC_OUT_DATA}" ]]
        LogInfo "XML file : No data to upload"
then
        for file in $(echo "${BEXEC_OUT_DATA}" | sed 's/ /g')
                if [[ -f ${file} ]]
                then
                        LogInfo "Upload [${file}]"
                        set -o pipefail
                        scp "${file}" "${LSB_SUB_HOST}:${CATALOGLOCATION}/${file}" 2>&1 | LogCMD
                        CR=$?
                        if [[ ${CR} -ne 0 ]]
                        then
                                LogInfo "Failed to transfer output file"
                                LogInfo "Transfer error [${CR}]."
                                [[ ! -z ${GLOBAL_TEMP} ]] && LogInfo "Moving files to ${GLOBAL_TEMP}" && mv * ${GLOBAL_TEMP}
                                EndOnError 80 "Transfer of output files with errors !!!!"
                        fi
                else
                        EndOnError 81 "Missing output file [${file}]"
                fi
        done
else
        LogInfo "No transfer done, results files are stored on [${PWD}]"
fi

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "Transfer output files"
# ------------------------------------------------------------------------------------------------------------------------

LogInfo "Databank content after execution :"
LogInfo "PATH : ${LOCALDB}"
(cd ${LOCALDB};find . -exec ls -ld "{}" ";" 2>&1) | LogCMD

LogUpload

if [[ "${TRANSFER}" = "yes" ]]
then
        cd "${LOCALDB}"
        for file in $(echo "${LSI_OUTPUT}" | sed 's/,/ /g')
        do
                if [[ -f ${file} ]]
                then
                        LogInfo "Upload [${file}]"
                        set -o pipefail
                        scp "${LOCALDB}/${file}" "${LSB_SUB_HOST}:${LSI_DATABANK}/${file}" 2>&1 | LogCMD
                        CR=$?
                        if [[ ${CR} -ne 0 ]]
                        then
                                LogInfo "Failed to transfer output file"
                                LogInfo "Transfer error [${CR}]."
                                [[ ! -z ${GLOBAL_TEMP} ]] && LogInfo "Moving files to ${GLOBAL_TEMP}" && mv * ${GLOBAL_TEMP}
                                EndOnError 80 "Transfer of output files with errors !!!!"
                        fi
                else
                        EndOnError 81 "Missing output file [${file}]"
                fi
        done
else
        LogInfo "No transfer done, results files are stored on [${PWD}]"
fi

# ------------------------------------------------------------------------------------------------------------------------
LogTitle "End of job"
# ------------------------------------------------------------------------------------------------------------------------

rm -fR ${LOCALDB}/data ${LOCALDB}/log ${LOCALDB}/tmp 1>/dev/null 2>&1

exit 0