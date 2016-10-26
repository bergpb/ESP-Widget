import networkimport socketimport ureimport timeimport gcimport hardwaresta = network.WLAN(network.STA_IF)ap = network.WLAN(network.AP_IF)machine_id = ""data_host = ""data_path = ""data_addr = ""last_message = ""message_ack = Falseerror_count = 0request_count = 0# ------------------------------------------------------# helper routines for doWidgetWork()# ------------------------------------------------------def setupStatus():    hardware.oled_clear()    hardware.oled_text("STATUS", 40, 0)    hardware.oled_text("UpTime :", 0, 8)    hardware.oled_text("FreeMem:", 0, 16)    from ubinascii import hexlify    hardware.oled_text("MAC:", 0, 24)    hardware.oled_text(hexlify(sta.config('mac')), 32, 24)    hardware.oled_text("ID:", 0, 32)    import machine    hardware.oled_text(hexlify(machine.unique_id()), 24, 32)    hardware.oled_text("IP:", 0, 40)    hardware.oled_text("GW:", 0, 48)    (address, mask, gateway, dns) = sta.ifconfig()    hardware.oled_text(address, 24, 40)    hardware.oled_text(gateway, 24, 48)def updateStatus():    hardware.oled_text(str(time.time()), 64, 8)    hardware.oled_text(str(gc.mem_free()), 64, 16)def setupWidget():    global data_host    global data_addr    global machine_id    global data_path    data_host = "wezensky.no-ip.org"    try:        data_addr = socket.getaddrinfo(data_host, 80)[0][-1]    except:        hardware.oled_text("Host Not Found", 8, 24)    import machine    from ubinascii import hexlify    machine_id = hexlify(machine.unique_id()).decode("utf-8")    data_path = machine_id + "/data.txt"# --------------------------------------------------------def updateWidget():        global data_addr    global data_host    global data_path    global message_ack    global error_count    global last_message    global request_count    request_count += 1    hardware.pixel_color(0, 32, 0)    resp = ""    try:        s = socket.socket()        s.connect(data_addr)        s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (data_path, data_host), 'utf8'))        while True:            data = s.recv(100)            if data:                resp += str(data, 'utf8')            else:                break        s.close()    except:        print("HTTP Get failed.")    if message_ack:        hardware.pixel_color(0, 0, 0)    else:        hardware.pixel_color(0, 0, 64)    if resp == "":        print("No content retrieved")                error_count += 1        if (error_count > 5):            print("Sleeping...")            time.sleep(120)            error_count = 0    else:        print(resp)        error_count = 0        lines = resp.split("\r\n")        linecount = len(lines)        content = "No content"        if linecount > 0:            content = ""            found = False            for line in range(linecount):                if lines[line] == "":                    found = True                else:                    if found:                        content += lines[line]        if last_message == "":            last_message = content            new_content = True        else:            if content == last_message:                            new_content = False            else:                last_message = content                new_content = True        if new_content:            message_ack = False            lines = content.split("/")            if len(lines) > 0:                if lines[0] == "t":                    hardware.oled_clear()                    for line in range(1, len(lines)):                        hardware.oled_text(lines[line], 0, 8 * (line - 1))                    hardware.pixel_color(0, 0, 64)                elif lines[0] == "p":                    last_red = int(lines[1])                    last_green = int(lines[2])                    last_blue = int(lines[3])                    hardware.pixel_color(last_red, last_green, last_blue)    gc.collect()    print(gc.mem_free())    print(request_count)# --------------------------------------------------------# will handle the display and the UI for the main function#---------------------------------------------------------def doWidgetWork():    global last_message    global message_ack    setupWidget()    current_screen = 0    refresh_deadline = 0    while True:        if current_screen == 0:            if time.time() > refresh_deadline:                updateWidget()                refresh_deadline = time.time() + 30        elif current_screen == 1:            updateStatus()        if hardware.button1_pressed():            if current_screen == 0:                current_screen = 1                setupStatus()            elif current_screen == 1:                current_screen = 0                last_message = ""                updateWidget()        if hardware.button2_pressed():            if current_screen == 1:                hardware.pixel_color(64, 64, 64)                sta.disconnect()                sta.connect("dummy", "")                sta.active(False)                break                    if hardware.button3_pressed():            hardware.pixel_color(0, 0, 0)            message_ack = True        gc.collect()