function popup(url) {
  newwindow=window.open(url,'name','height=400,width=600');
  if (window.focus) newwindow.focus();
  return false;
}
function collapse(id) { $('#'+id).slideToggle(); }
function fade(id,value) { if(value>0) $('#'+id).hide().fadeIn('slow'); else $('#'+id).show().fadeOut('slow'); }
function ajax(u,s,t) {
  var query="";
  for(i=0; i<s.length; i++) { 
     if(i>0) query=query+"&";
     query=query+encodeURIComponent(s[i])+"="+encodeURIComponent(document.getElementById(s[i]).value);
  }
  $.ajax({type: "POST", url: u, data: query, success: function(msg) { document.getElementById(t).innerHTML=msg; } });  
}
String.prototype.reverse = function () { return this.split('').reverse().join('');};
$(document).ready(function() {
$('.hidden').hide();
$('.error').hide().slideDown('slow');
$('.flash').hide().slideDown('slow')
$('.flash').click(function() { $(this).fadeOut('slow'); return false; });
$('input.string').attr('size',50);
$('textarea.text').attr('cols',50).attr('rows',10);
$('input.integer').keyup(function(){this.value=this.value.reverse().replace(/[^0-9\-]|\-(?=.)/g,'').reverse();});
$('input.double').keyup(function(){this.value=this.value.reverse().replace(/[^0-9\-\.]|[\-](?=.)|[\.](?=[0-9]*[\.])/g,'').reverse();});
$('input.delete').attr('onclick','if(this.checked) if(!confirm("Sure you want to delete this object?")) this.checked=false;');
try {$("input.date").focus( function() {Calendar.setup({
     inputField:this.id, ifFormat:"%Y-%m-%d", showsTime:false
}); }); } catch(e) {};
try { $("input.datetime").focus( function() {Calendar.setup({
     inputField:this.id, ifFormat:"%Y-%m-%d %H:%M:%S", showsTime: true,timeFormat: "24"
}); }); } catch(e) {};
try { $("input.time").clockpick({
     starthour:0, endhour:23, showminutes:true, military:true
}); } catch(e) {};
try { $('.zoom').fancyZoom({scaleImg:true, closeOnClick:true, directory:"/plugin_t2/static/t2/media"}); } catch(e) {};
try { $('.sf-menu').superfish({
     animation: {height:'show'}, delay:1200
}); } catch(e) {};
});
