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
import os

config.misc.ci_auto_check_module = ConfigYesNo(False)

ciplushelper = "/etc/init.d/ciplushelper"

version = "4"

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
		list = []
		list.append((_("Supported models"), "about_ciplushelper"))
		model = ""
		if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/info.txt"):
			try:
				f = open('/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/info.txt', 'r')
				lines = f.read()
				if "ciplushelper-arm" in lines:
					model = "ciplushelper-arm"
				elif "ciplushelper-mipsel32" in lines:
					model = "ciplushelper-mipsel32"
				f.close()
			except:
				pass
		self.ret = os.popen("top -n 1").read()
		if model:
			if os.path.exists("/etc/rc2.d/S50ciplushelper"):
				list.append((_("Disable ciplushelper autostart"), "disable"))
			else:
				list.append((_("Enable ciplushelper autostart"), "enable"))
			if "ciplushelper" in self.ret:
				list.append((_("Stop ciplushelper"), "stop"))
			else:
				list.append((_("Start ciplushelper"), "start"))
			if "ciplushelper-arm" in model:
				if not os.path.exists("/etc/cicert.bin"):
					list.append((_("Install 'ciplushelper' version from Zgemma"), "install_cicert_bin"))
				else:
					if os.path.exists("/etc/ciplus0_enable"):
						list.append((_("Enable '/etc/ciplus0_enable'"), "disable_ciplus0"))
					elif os.path.exists("/etc/ciplus0_disable"):
						list.append((_("Disable '/etc/ciplus0_disable'"), "enable_ciplus0"))
					if os.path.exists("/etc/ciplus1_enable"):
						list.append((_("Enable '/etc/ciplus1_enable'"), "disable_ciplus1"))
					elif os.path.exists("/etc/ciplus1_disable"):
						list.append((_("Disable '/etc/ciplus1_disable'"), "enable_ciplus1"))
					list.append((_("Install default version 'ciplushelper'"), "install_default"))
			try:
				copy = True
				f = open('/etc/init.d/ciplushelper', 'r')
				lines = f.read()
				if "VERSION=1" in lines:
					copy = False
				f.close()
				if copy:
					cmd = "cp /usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/ciplushelper.sh %s && chmod 755 %s" % (ciplushelper, ciplushelper)
					os.system(cmd)
			except:
				pass
		#if config.misc.ci_auto_check_module.value:
		#	list.append((_("'Off' auto check module after start E2 (delay 60 sec.)"), "auto_check"))
		#else:
		#	list.append((_("'On' auto check module after start E2 (delay 60 sec.)"), "auto_check"))
		if os.path.exists("/etc/ciplus/customer.pem") and os.path.exists("/etc/ciplus/device.pem") and os.path.exists("/etc/ciplus/root.pem") and os.path.exists("/etc/ciplus/param"):
			list.append((_("Remove '/etc/ciplus'"), "remove_sert"))
		else:
			list.append((_("Install '/etc/ciplus'"), "install_sert"))
		self["menu"] = MenuList(list)
		self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.run, "cancel": self.close}, -1)

	def run(self):
		returnValue = self["menu"].l.getCurrentSelection() and self["menu"].l.getCurrentSelection()[1]
		if returnValue != None:
			if returnValue == "enable":
				self.session.open(Console,_("Enable ciplushelper autostart"), ["%s enable_autostart" % ciplushelper])
				self.close()
			elif returnValue == "disable":
				self.session.open(Console,_("Disable ciplushelper autostart"), ["%s disable_autostart" % ciplushelper])
				self.close()
			elif returnValue == "start":
				self.session.open(Console,_("Start ciplushelper"), ["%s start" % ciplushelper])
				self.close()
			elif returnValue == "stop":
				self.session.open(Console,_("Stop ciplushelper"), ["%s stop" % ciplushelper])
				self.close()
			elif returnValue == "auto_check":
				config.misc.ci_auto_check_module.value = not config.misc.ci_auto_check_module.value
				config.misc.ci_auto_check_module.save()
				self.close()
			elif returnValue == "install_sert":
				cmd = "cp -R /usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/ciplus /etc/ciplus"
				os.system(cmd)
				self.close()
			elif returnValue == "install_cicert_bin":
				cmd = "cp /usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/cicert.bin /etc/cicert.bin"
				os.system(cmd)
				if not os.path.exists("/etc/ciplus0_enable") or not os.path.exists("/etc/ciplus0_disable"):
					cmd = "echo 'rename ciplus*_enable to ciplus*_disable for deactivate ciplus certification of the module.' > /etc/ciplus0_enable"
					os.system(cmd)
				if not os.path.exists("/etc/ciplus1_enable") or not os.path.exists("/etc/ciplus1_disable"):
					cmd = "echo 'rename ciplus*_enable to ciplus*_disable for deactivate ciplus certification of the module.' > /etc/ciplus1_enable"
					os.system(cmd)
				cmd1 = ""
				if "ciplushelper" in self.ret:
					cmd1 = "killall ciplushelper 2>/dev/null && sleep 2"
					os.system(cmd1)
				cmd = "cp /usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/ciplushelper_bin/zgemma-arm/ciplushelper /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper"
				os.system(cmd)
				if cmd1:
					self.session.open(Console,_("Start ciplushelper"), ["/etc/init.d/ciplushelper start && echo 'Need restart GUI'"])
				self.close()
			elif returnValue == "install_default":
				cmd = "rm -rf /etc/cicert.bin"
				os.system(cmd)
				cmd1 = ""
				if "ciplushelper" in self.ret:
					cmd1 = "killall ciplushelper 2>/dev/null && sleep 2"
					os.system(cmd1)
				cmd = "cp /usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/ciplushelper_bin/arm/ciplushelper /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper"
				os.system(cmd)
				if cmd1:
					self.session.open(Console,_("Start ciplushelper"), ["/etc/init.d/ciplushelper start && echo 'Need restart GUI'"])
				self.close()
			elif returnValue == "remove_sert":
				cmd = "rm -rf /etc/ciplus"
				os.system(cmd)
				self.close()
			elif returnValue == "disable_ciplus0":
				cmd = "mv /etc/ciplus0_enable /etc/ciplus0_disable"
				os.system(cmd)
				self.close()
			elif returnValue == "enable_ciplus0":
				cmd = "mv /etc/ciplus0_disable /etc/ciplus0_enable"
				os.system(cmd)
				self.close()
			elif returnValue == "disable_ciplus1":
				cmd = "mv /etc/ciplus1_enable /etc/ciplus1_disable"
				os.system(cmd)
				self.close()
			elif returnValue == "enable_ciplus1":
				cmd = "mv /etc/ciplus1_disable /etc/ciplus1_enable"
				os.system(cmd)
				self.close()
			elif returnValue == "about_ciplushelper":
				self.session.open(MessageBox, _("Support '/usr/bin/ciplushelper' from the manufacturer:\n") + "HD51 / VS1500 / Zgemma (H6/H7/H9combo(se)/H9twin(se)/H10) / Mutant (hd1500/hd2400) / Xtrend (et8000/et10000) / Formuler (f1/f3/f4) / Pulse 4K(mini)\n" + _("Other models need '/etc/ciplus'"), MessageBox.TYPE_INFO)

pause_checkTimer = eTimer()

def check_cimodule():
	try:
		NUM_CI = SystemInfo["CommonInterface"]
		if NUM_CI:
			change = False
			if NUM_CI == 1:
				state = eDVBCI_UI.getInstance().getState(0)
				if state == 1:
					SystemInfo["CommonInterface"] = 0
					change = True
			elif NUM_CI == 2:
				state = eDVBCI_UI.getInstance().getState(0)
				state1 = eDVBCI_UI.getInstance().getState(1)
				if state == 1 and state1 == 2:
					return
				if state == 1:
					SystemInfo["CommonInterface"] -= 1
					change = True
				if state1 == 1:
					SystemInfo["CommonInterface"] -= 1
					change = True
			if change:
				pass
				try:
					from Tools.CIHelper import cihelper
					cihelper.load_ci_assignment(force=True)
				except:
					pass
				try:
					if _Session and _Session.nav.getCurrentlyPlayingServiceOrGroup():
						_Session.nav.playService(_Session.nav.getCurrentlyPlayingServiceOrGroup(), forceRestart=True)
				except:
					pass
	except:
		pass

_Session = None

def sessionstart(reason, session):
	pass
	#if reason == 0 and session and config.misc.ci_auto_check_module.value:
	#	ret = os.popen("top -n 1").read()
	#	if "ciplushelper" in ret:
	#		global _Session
	#		_Session = session
	#		pause_checkTimer.stop()
	#		pause_checkTimer.start(60000, True)

pause_checkTimer.callback.append(check_cimodule)

def main(session, **kwargs):
	session.open(Ciplushelper)

def menu(menuid, **kwargs):
	if menuid == "cam":
		return [(_("CI+ helper"), main, "ci_helper", 30)]
	return []

def Plugins(**kwargs):
	if SystemInfo["CommonInterface"]:
		return [PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, needsRestart = False, fnc = sessionstart),
				PluginDescriptor(name = _("CI+ helper"), description = "", where = PluginDescriptor.WHERE_MENU, needsRestart = False, fnc = menu)]
	return []

