#!/bin/sh
#
# nfquery plugin installation script.

err () {
	echo "ERROR: ${*}"
	exit 1
}

echo "NfQuery Plugin Installation Script"
echo "----------------------------------"

# Discover NfSen configuration
NFSEN_VARFILE=/tmp/nfsen-tmp.conf
if [ ! -n "$(ps axo command | grep [n]fsend | grep -v nfsend-comm)" ]; then
	err "NfSen - nfsend not running. Can not detect nfsen.conf location!"
fi

NFSEN_LIBEXECDIR=$(cat $(ps axo command= | grep [n]fsend | grep -v nfsend-comm | cut -d' ' -f3) | grep libexec | cut -d'"' -f2)
NFSEN_CONF=$(cat ${NFSEN_LIBEXECDIR}/NfConf.pm | grep \/nfsen.conf | cut -d'"' -f2)

# Parse nfsen.conf file
cat ${NFSEN_CONF} | grep -v \# | egrep '\$BASEDIR|\$BINDIR|\$HTMLDIR|\$FRONTEND_PLUGINDIR|\$BACKEND_PLUGINDIR|\$WWWGROUP|\$WWWUSER|\$USER' | tr -d ';' | tr -d ' ' | cut -c2- | sed 's,/",",g' > ${NFSEN_VARFILE}
. ${NFSEN_VARFILE}
rm -rf ${NFSEN_VARFILE}


# Check permissions to install nfquery plugin - you must be ${USER} or root
if [ "$(id -u)" != "$(id -u ${USER})" ] && [ "$(id -u)" != "0" ]; then
	err "You do not have sufficient permissions to install nfquery on this server!"
fi

if [ "$(id -u)" = "$(id -u ${USER})" ]; then
	WWWUSER=${USER}		# we are installing as normal user
fi

# Backup old nfquery installation
if [ -d ${FRONTEND_PLUGINDIR}/nfquery ]; then
	NFQUERY_BACKUPDIR=${FRONTEND_PLUGINDIR}/nfquery-$(date +%s)
	echo "Backuping old nfquery installation to ${NFQUERY_BACKUPDIR}"
	mv ${FRONTEND_PLUGINDIR}/nfquery ${NFQUERY_BACKUPDIR}
fi

# Install backend and frontend plugin files
echo "Installing nfquery to ${FRONTEND_PLUGINDIR}/nfquery"
cp -r ./backend/* ${BACKEND_PLUGINDIR}
cp -r ./frontend/* ${FRONTEND_PLUGINDIR}

# Set permissions - owner and group
echo "Setting plugin files permissions - user \"${USER}\" and group \"${WWWGROUP}\""
chown -R ${USER}:${WWWGROUP} ${FRONTEND_PLUGINDIR}/nfquery*
chown -R ${USER}:${WWWGROUP} ${BACKEND_PLUGINDIR}/nfquery*
chmod g+w ${FRONTEND_PLUGINDIR}/nfquery/remember.conf


echo ""

# Restart/reload NfSen
echo "Please restart/reload NfSen to finish installation (e.g. sudo ${BINDIR}/nfsen reload)"

