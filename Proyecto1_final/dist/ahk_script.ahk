
#Persistent
#SingleInstance force

; Script de AutoHotkey para manejar acciones de UI
Loop {
    ; Esperar comandos de Python
    FileRead, comando, ahk_command.txt
    if (ErrorLevel = 0) {
        FileDelete, ahk_command.txt
        
        ; Parsear comando: x,y,filename
        Array := StrSplit(comando, ",")
        x_campo := Array[1]
        y_campo := Array[2]
        nombre_archivo := Array[3]
        
        ; Ejecutar acciones
        Click, %x_campo% %y_campo%
        Sleep, 200
        
        ; Limpiar campo
        Send, ^a
        Sleep, 100
        Send, {Delete}
        Sleep, 100
        
        ; Escribir nombre de archivo (método confiable)
        SendInput, %nombre_archivo%
        Sleep, 400
        
        ; Presionar Enter
        Send, {Enter}
        Sleep, 200
        
        ; Confirmación para Python
        FileAppend, done, ahk_done.txt
        FileDelete, ahk_done.txt
    }
    Sleep, 500  ; Revisar cada medio segundo
}
