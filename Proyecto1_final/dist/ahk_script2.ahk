
#Persistent
#SingleInstance force

; Script de AutoHotkey para presionar Enter múltiples veces
Loop {
    ; Esperar comandos de Python
    FileRead, comando, ahk_command.txt
    if (ErrorLevel = 0) {
        FileDelete, ahk_command.txt
        
        ; Parsear comando: numero_de_veces
        veces := comando
        
        ; Presionar Enter el número de veces especificado
        Loop, %veces% {
            Send, {Enter}
            Sleep, 600  ; Pausa entre cada Enter
        }
        
        ; Confirmación para Python
        FileAppend, done, ahk_done.txt
        FileDelete, ahk_done.txt
    }
    Sleep, 500  ; Revisar cada medio segundo
}
