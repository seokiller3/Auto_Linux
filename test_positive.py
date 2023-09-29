import yaml
from checkers import getout
from sshcheckers import ssh_checkout, upload_files, ssh_getout

with open('config.yaml') as f:
    # читаем YAML document
    data = yaml.safe_load(f)


class TestPositive:

    def save_log(self, starttime, name):
        with open(name, 'w') as f:
            f.write(getout(f"journalctl --since '{starttime}'"))

    def test_step1(self, start_time):

        res = []
        upload_files(data["ip"], data["user"], data["passwd"], f"{data['pkgname']}.deb",
                     f"/home/{data['user']}/{data['pkgname']}.deb")
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"],
                                f"echo '{data['passwd']}' | sudo -S dpkg -i /home/{data['user']}/{data['pkgname']}.deb",
                                "Настраивается пакет"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"],
                                f"echo '{data['passwd']}' | sudo -S dpkg -s {data['pkgname']}",
                                "Status: install ok installed"))
        self.save_log(start_time, "log1.txt")
        assert all(res), "test1 FAIL"

    def test_step2(self, make_folders, clear_folders, make_files, start_time):
        """проверка команды a (архивирования)"""
        res1 = ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_in']};"
                                                                      f" 7z a {data['folder_out']}/arx2",
                            "Everything is Ok")
        res2 = ssh_checkout(data["ip"], data["user"], data["passwd"], f"ls {data['folder_out']}", "arx2.7z")
        self.save_log(start_time, "log2.txt")
        assert res1 and res2, "test2 FAIL"

    def test_step3(self, clear_folders, make_files, start_time):
        """проверка команды e (разархивирования)"""
        res = []
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_in']}; "
                                                                          f"7z a {data['folder_out']}/arx2",
                                "Everything is Ok"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_out']}; "
                                                                          f"7z e arx2.7z -o{data['folder_ext']} -y",
                                "Everything is Ok"))
        for item in make_files:
            res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f"ls {data['folder_ext']}", item))
        self.save_log(start_time, "log3.txt")
        assert all(res), "test3 FAIL"

    def test_step2_1(self):
        """дополнительная проверка создания файла во время архивирования"""
        res = []
        res.append(self.ssh_checkout(f"cd {data['folder_out']}; 7z a ../out/арх2 test_file.txt", "Everithing is ok"))
        res.append(self.ssh_checkout(f"ls {data['folder_out']};", "арх2.7z"))
        assert all(res), "test 2_1 FAIL"

    def test_step3_1(self):
        """проверка создания файла во время распаковки"""
        res = []
        res.append(
            self.ssh_checkout(f"cd {data['folder_out']}; 7z e арх2.7z -o{data['folder_ext']}", "Everithing is ok"))
        res.append(self.ssh_checkout(f"ls {data['folder_out']};", "тестовый_файл.txt"))
        assert all(res), "test 3_1 FAIL"

    def test_step4(self, start_time):
        """проверка команды t (проверка целостности архива)"""
        self.save_log(start_time, "log4.txt")
        assert ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_out']}; "
                                                                      f"7z t arx2.7z", "Everything is Ok"), "test4 FAIL"

    def test_step5(self, start_time):
        """проверка команды u (обновление архива)"""
        self.save_log(start_time, "log5.txt")
        assert ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_in']}; "
                                                                      f"7z u arx2.7z", "Everything is Ok"), "test5 FAIL"

    def test_step6(self, clear_folders, make_files, start_time):
        """проверка команды l (список файлов)"""
        res = []
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_in']}; "
                                                                          f"7z a {data['folder_out']}/arx2",
                                "Everything is Ok"))
        for item in make_files:
            res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_out']}; "
                                                                              f"7z l arx2.7z", item))
        self.save_log(start_time, "log6.txt")
        assert all(res), "test6 FAIL"

    def test_step7(self, clear_folders, make_files, make_subfolder, start_time):
        res = []
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_in']}; "
                                                                          f"7z a {data['folder_out']}/arx",
                                "Everything is Ok"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_out']}; "
                                                                          f"7z x arx.7z -o{data['folder_ext2']} -y",
                                "Everything is Ok"))

        for item in make_files:
            res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f"ls {data['folder_ext2']}", item))

            res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f"ls {data['folder_ext2']}",
                                    make_subfolder[0]))
            res.append(
                ssh_checkout(data["ip"], data["user"], data["passwd"], f"ls {data['folder_ext2']}/{make_subfolder[0]}",
                             make_subfolder[1]))

        self.save_log(start_time, "log7.txt")
        assert all(res), "test7 FAIL"

    def test_step8(self, start_time):
        """проверка команды d (удаление из архива)"""
        self.save_log(start_time, "log8.txt")
        assert ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_out']}; 7z d arx.7z",
                            "Everything is Ok"), "test8 FAIL"

    def test_step9(self, clear_folders, make_files, start_time):
        self.save_log(start_time, "log9.txt")
        res = []
        for item in make_files:
            res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_in']}; 7z h {item}",
                                    "Everything is Ok"))
            hash = ssh_getout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_in']}; "
                                                                        f"crc32 {item}").upper()
            res.append(
                ssh_checkout(data["ip"], data["user"], data["passwd"], f"cd {data['folder_in']}; 7z h {item}", hash))
        assert all(res), "test9 FAIL"

    def test_step10(self, start_time):
        res = []
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"],
                                f"echo '{data['passwd']}' | sudo -S dpkg -r {data['pkgname']}",
                                "Удаляется"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"],
                                f"echo '{data['passwd']}' | sudo -S dpkg -s {data['pkgname']}",
                                "Status: deinstall ok"))
        assert all(res), "test10 FAIL"
