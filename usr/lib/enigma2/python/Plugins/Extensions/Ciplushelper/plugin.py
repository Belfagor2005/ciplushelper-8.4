#!/usr/bin/python
from . import _

from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.SystemInfo import SystemInfo
from enigma import eTimer, eDVBCI_UI, getDesktop
from Components.config import config, ConfigYesNo
from os import popen, system
from os.path import exists, join
config.misc.ci_auto_check_module = ConfigYesNo(False)

version = "1"
plugin_path = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper"
info_path = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/info.txt"
ciplushelper_sh = join(plugin_path, "ciplushelper.sh")
ciplushelper = "/etc/init.d/ciplushelper"


class Ciplushelper(Screen):
	if getDesktop(0).size().width() >= 1920:
		skin = """
		<screen position="center,center" size="1020,280" title="CI+ helper menu" >
			<widget name="menu" position="10,10" size="1000,260" font="Regular;30" itemHeight="36" scrollbarMode="showOnDemand" />
		</screen>"""
	else:
		skin = """
		<screen position="center,center" size="670,180" title="CI+ helper menu" >
			<widget name="menu" position="10,10" size="660,160" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.setTitle(_("CI+ helper menu") + ": " + _("ver.") + version)

		menu_list = []
		menu_list.append((_("Supported models"), "about_ciplushelper"))
		model = ""

		if exists(info_path):
			try:
				with open(info_path, "r") as f:
					lines = f.read()
					if "ciplushelper-arm" in lines:
						model = "ciplushelper-arm"
					elif "ciplushelper-mipsel32" in lines:
						model = "ciplushelper-mipsel32"
			except IOError:
				pass

		self.ret = popen("pgrep ciplushelper").read()
		if model:
			menu_list.append(
				(_("Disable ciplushelper autostart"), "disable")
				if exists("/etc/rc2.d/S50ciplushelper")
				else (_("Enable ciplushelper autostart"), "enable")
			)
			menu_list.append(
				(_("Stop ciplushelper"), "stop")
				if "ciplushelper" in self.ret
				else (_("Start ciplushelper"), "start")
			)

			if model == "ciplushelper-arm":
				if not exists("/etc/cicert.bin"):
					menu_list.append((_("Install 'ciplushelper' version from Zgemma"), "install_cicert_bin"))
				else:
					for i in range(2):
						enable_file = "/etc/ciplus%d_enable" % i
						disable_file = "/etc/ciplus%d_disable" % i
						if exists(enable_file):
							menu_list.append((_("Enable '%s'") % enable_file, "disable_ciplus%d" % i))
						elif exists(disable_file):
							menu_list.append((_("Disable '%s'") % disable_file, "enable_ciplus%d" % i))

					menu_list.append((_("Install default version 'ciplushelper'"), "install_default"))

			try:
				copy = True
				with open("/etc/init.d/ciplushelper", "r") as f:
					if "VERSION=1" in f.read():
						copy = False

				if copy:
					cmd = "cp {} {} && chmod 755 {}".format(ciplushelper_sh, ciplushelper, ciplushelper)
					system(cmd)
			except IOError:
				pass

		if exists("/etc/ciplus/customer.pem") and exists("/etc/ciplus/device.pem") and exists("/etc/ciplus/root.pem") and exists("/etc/ciplus/param"):
			menu_list.append((_("Remove '/etc/ciplus'"), "remove_sert"))
		else:
			menu_list.append((_("Install '/etc/ciplus'"), "install_sert"))

		self["menu"] = MenuList(menu_list)
		self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.run, "cancel": self.close}, -1)

	def run(self):
		returnValue = self["menu"].l.getCurrentSelection()
		if returnValue:
			returnValue = returnValue[1]
			commands = {
				"enable": "{} enable_autostart".format(ciplushelper),
				"disable": "{} disable_autostart".format(ciplushelper),
				"start": "{} start".format(ciplushelper),
				"stop": "{} stop".format(ciplushelper),
				"install_sert": "cp -R {}/ciplus /etc/ciplus".format(plugin_path),
				"install_cicert_bin": "cp {}/cicert.bin /etc/cicert.bin".format(plugin_path),
				"install_default": "rm -rf /etc/cicert.bin",
				"remove_sert": "rm -rf /etc/ciplus",
				"disable_ciplus0": "mv /etc/ciplus0_enable /etc/ciplus0_disable",
				"enable_ciplus0": "mv /etc/ciplus0_disable /etc/ciplus0_enable",
				"disable_ciplus1": "mv /etc/ciplus1_enable /etc/ciplus1_disable",
				"enable_ciplus1": "mv /etc/ciplus1_disable /etc/ciplus1_enable",
			}

			if returnValue in commands:
				system(commands[returnValue])
				self.close()
				return

			if returnValue == "auto_check":
				config.misc.ci_auto_check_module.value = not config.misc.ci_auto_check_module.value
				config.misc.ci_auto_check_module.save()
				self.close()
				return

			if returnValue == "install_cicert_bin":
				for i in range(2):
					file_enable = "/etc/ciplus%d_enable" % i
					file_disable = "/etc/ciplus%d_disable" % i
					if not exists(file_enable) or not exists(file_disable):
						system("echo 'rename ciplus*_enable to ciplus*_disable for deactivate ciplus certification of the module.' > %s" % file_enable)

				if "ciplushelper" in self.ret:
					system("killall ciplushelper 2>/dev/null && sleep 2")

				system("cp {}/ciplushelper_bin/zgemma-arm/ciplushelper /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper".format(plugin_path))

				if "ciplushelper" in self.ret:
					self.session.open(Console, _("Start ciplushelper"), ["/etc/init.d/ciplushelper start && echo 'Need restart GUI'"])
				self.close()
				return

			if returnValue == "install_default":
				if "ciplushelper" in self.ret:
					system("killall ciplushelper 2>/dev/null && sleep 2")

				system("cp {} /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper".format(
					join(plugin_path, "ciplushelper_bin", "arm", "ciplushelper")
				))

				if "ciplushelper" in self.ret:
					self.session.open(Console, _("Start ciplushelper"), ["/etc/init.d/ciplushelper start && echo 'Need restart GUI'"])
				self.close()
				return

			if returnValue == "about_ciplushelper":
				message = _("Support '/usr/bin/ciplushelper' from the manufacturer:\n") + \
					"HD51 / VS1500 / Zgemma (H6/H7/H9combo(se)/H9twin(se)/H10) / Mutant (hd1500/hd2400) / Xtrend (et8000/et10000) / Formuler (f1/f3/f4) / Pulse 4K(mini)\n" + \
					_("Other models need '/etc/ciplus'")
				self.session.open(MessageBox, message, MessageBox.TYPE_INFO)


pause_checkTimer = eTimer()


def check_cimodule():
	try:
		NUM_CI = SystemInfo["CommonInterface"]
		if not NUM_CI:
			return

		ci_ui = eDVBCI_UI.getInstance()
		change = False

		if NUM_CI == 1:
			if ci_ui.getState(0) == 1:
				SystemInfo["CommonInterface"] = 0
				change = True

		elif NUM_CI == 2:
			state0 = ci_ui.getState(0)
			state1 = ci_ui.getState(1)

			if state0 == 1 and state1 == 2:
				return

			if state0 == 1 or state1 == 1:
				SystemInfo["CommonInterface"] -= (state0 == 1) + (state1 == 1)
				change = True

		if change:
			try:
				from Tools.CIHelper import cihelper
				cihelper.load_ci_assignment(force=True)
			except ImportError:
				pass

			try:
				if _Session and _Session.nav.getCurrentlyPlayingServiceOrGroup():
					# Restart the currently playing service if required
					_Session.nav.playService(_Session.nav.getCurrentlyPlayingServiceOrGroup(), forceRestart=True)
			except AttributeError:
				pass

	except KeyError:
		pass


_Session = None


def sessionstart(reason, session):
	pass

	"""
	if reason == 0 and session and config.misc.ci_auto_check_module.value:
		ret = os.popen("top -n 1").read()
		if "ciplushelper" in ret:
			global _Session
			_Session = session
			pause_checkTimer.stop()
			pause_checkTimer.start(60000, True)
	"""


pause_checkTimer.callback.append(check_cimodule)


def main(session, **kwargs):
	session.open(Ciplushelper)


def menu(menuid, **kwargs):
	if menuid == "cam":
		return [(_("CI+ helper"), main, "ci_helper", 30)]
	return []


def Plugins(**kwargs):
	if SystemInfo["CommonInterface"]:
		return [
			PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, needsRestart=False, fnc=sessionstart),
			PluginDescriptor(name=_("CI+ helper"), description="", where=PluginDescriptor.WHERE_MENU, needsRestart=False, fnc=menu)
		]
	return []
