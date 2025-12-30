#Persistent
#SingleInstance force

; Script de AutoHotkey para guardar con Ctrl+S
Loop {
    ; Esperar comandos de Python
    FileRead, comando, ahk_save_command.txt
    if (ErrorLevel = 0) {
        FileDelete, ahk_save_command.txt
        
        ; Parsear comando: acción
        accion := Trim(comando)
        
        ; Ejecutar acción de guardar
        if (accion = "SAVE") {
            ; Enviar Ctrl+S para guardar
            Send, ^s
            Sleep, 1000
            
            ; Confirmación para Python
            FileDelete, ahk_savedone.txt  ; <<< CAMBIÉ EL NOMBRE AQUÍ
            FileAppend, saved, ahk_savedone.txt  ; <<< Y AQUÍ
            Sleep, 300
            ; No borramos aquí, Python lo hará
        }
    }
    Sleep, 500  ; Revisar cada medio segundo
}