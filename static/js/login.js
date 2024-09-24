function showPassword(name){
    let passwordShow=document.getElementById(""+ name + '_password');
    let show=document.getElementById('bx-show-' + name + "");
    let hide=document.getElementById('bx-hide-' + name + "");
    passwordShow.type="text";
    show.style.display="block";
    hide.style.display="none";
}
function hidePassword(name){
    let passwordShow=document.getElementById("" + name + '_password');
    let show=document.getElementById('bx-show-' + name + "" );
    let hide=document.getElementById('bx-hide-' + name + "");
    passwordShow.type="password";
    show.style.display="none";
    hide.style.display="block";
}