var NODE = document;
var EDO = new Object();

// 获取以class进行传参的值(kssattr-param1-false)
var _getValueFromEncodings = function(encodings, prefix) {
     prefix = prefix + '-';
     var prefixLength = prefix.length;
     for (var i = 0; i < encodings.length; i ++) {
         var encoding = encodings[i];
         if (encoding.substr(0, prefixLength) == prefix) {
             return encoding.substr(prefixLength);
         }
     }
     return undefined;
};

// 获取绝对地址调用
var _getURL = function(url) {
     if (/^http[s]?:/i.test(url)) {
         return url;
     }
     else {
         var baseURL = $('base').attr('href');
         var lastChar = baseURL.charAt(baseURL.length - 1);
         if (lastChar == '/') {
             return baseURL + url;
         }
         else {
             return baseURL + '/' + url;
         }
     }
};
// 对应kss的attr方法
var _getAttr = function(node, attr) {
     var parentnode = $(node);
     var value;
     var num = 0;
     while (true) {
         if (num > 14) { break; }
         value = parentnode.attr('kssattr:' + attr);
         if (value === undefined) {
             var $jlass = parentnode.attr('class');
             if ($jlass) {
                 var splitclass = $jlass.split(/ +/);
                 value = _getValueFromEncodings(splitclass, 'kssattr-' + attr);
             }
             if (value === undefined) {
                 num = num + 1;
                 parentnode = parentnode.parent();
             } else { break; }
         } else { break; }
     }
     return value;
};
// Ajax出错后给出提示
var _errorAjax = function(eventData) {
     var statuscode = eventData.status;
     if (statuscode == 500) {
         var statusText = eventData.statusText == 'KeyError' ? '页面相关的对象找不到，可能已经被删除。' : '500 系统发生故障';
         $().message(statusText, 'warning');
     }
     else if (statuscode == 404) {
         $().message('404 该链接不存在', 'warning');
     }
     else if (statuscode == 403) {
         if (eventData.statusText == 'UnLicensedError'){
            var statusText = '您没有授权使用此服务，请和管理员联系。';
         }
         else if (eventData.statusText == 'Logout'){
            var statusText = '403 由于您没有登录或者账号超时自动登出，没有权限 <a style="margin-left:5px;" href=".">重新登录</a>';
         }
         else{
            var statusText = '403 没有访问权限';
         }
         $().message(statusText, 'warning');
     }
     else if (statuscode == 401) {
         $().message('401 没有访问权限', 'warning');
     }
     else if (statuscode == 413) {
         $().message('413 容量超过配额', 'warning');
     }
     else if (statuscode == 0) {
         $().message('网络连接错误，请稍候重试。', 'warning');
     }
};

/*------------------------------------------------------------------------------------------------------------*/

(function($) {
   $.fn.kss = function(url, params, method) {
     if (url instanceof Object) {
         var options = url;
     } else {
         var options = {
           url: url,
           params: params
         };
     }

     var defaults = {
       url: null,
       params: undefined,
       mask: false
     };
     var opts = $.extend(defaults, options);

     if (opts.mask) ajaxLoad();

     $('#jqueryMessage').hide();

     NODE = this;
     var url = _getURL(opts.url);

     $.ajax({
       type: method || (opts.params ? 'POST' : 'GET'),
       url: url,
       data: opts.params,
       headers: {'Kss': true},
       success: function(script) {
           //new Function(script)();
       },
       error: function(eventData) {
           _errorAjax(eventData);
       },
       complete: function() {
           cancelLoad();
       }
     });
   };
})(jQuery);
/* XXX kssServerAction 函数过时 */
function kssServerAction (node, actionURL, params, spinnerid, mask) {
     var $spinnerid;
     if (spinnerid) {
         $spinnerid = $('#' + spinnerid);
         $spinnerid.removeClass('hidden');
     }

     $(node).kss({
       url: actionURL,
       params: params,
       mask: mask
     });

     if ($spinnerid) $spinnerid.addClass('hidden');
};
/* KSSLoad模式 */
function kssLoading (node, content) {
     if (!node.length) { return; }
     if (node[0].tagName == 'INPUT') {
         node.val(content);
     }
     else {
          node.html(content);
     }
     node.attr('disabled', true).css('cursor', 'auto');

}
/* 恢复KSSLoad模式 */
function recoveryLoad (node, content) {
     if (!node.length) { return; }
     if (node[0].tagName == 'INPUT') {
         node.val(content);
     }
     else {
          node.html(content);
     }
     node.attr('disabled', false).css('cursor', 'pointer');
};
/* 得到load前内容 */
function getLoadDefaultContent(node) {
     if (!node.length) { return; }
     if (node[0].tagName == 'INPUT') {
         return node.val();
     }
     else {
         return node.html();
     }
};

$(function(){
    var win = window, na = navigator, ua = na.userAgent;
    EDO.isIE11 = ua.indexOf('Trident/') != -1 && (ua.indexOf('rv:') != -1 || na.appName.indexOf('Netscape') != -1);
    EDO.isOpera = win.opera && opera.buildNumber;
    EDO.isWebKit = /WebKit/.test(ua);
    EDO.isIE = !EDO.isWebKit && !EDO.isOpera && (/MSIE/gi).test(ua) && (/Explorer/gi).test(na.appName) || EDO.isIE11;
    EDO.isIE6 = EDO.isIE && /MSIE [56]/.test(ua);
    EDO.isIE7 = EDO.isIE && /MSIE [7]/.test(ua);
    EDO.isIE8 = EDO.isIE && /MSIE [8]/.test(ua);
    EDO.isIE9 = EDO.isIE && /MSIE [9]/.test(ua);
    EDO.isMobile =  /android|iphone|ipod|series60|symbian|windows ce|blackberry/i.test(ua);
    EDO.lang = $('html').attr('lang');

    /* ActionServer模式 */
    $('body').on('click', '.KSSActionServer, .kss', function(event) {
         if (this.tagName == 'FORM') { return; }
         // 是否有KSSLoad模式
         var $load = $(this).hasClass('KSSLoad');
         var $load_node = $(this);
         if ($load == false) {
             if ($(this).find('.KSSLoad').length != 0) {
                 $load = true;
                 $load_node = $(this).find('.KSSLoad');
             }
         }
         var $load_text = '';
         var $load_default_content = getLoadDefaultContent($load_node);
         if ($load) {
              $load_text = _getAttr($load_node, 'loading_text') || $load_node.data('loading') || '...';
              kssLoading($load_node, $load_text);
         } else { ajaxLoad(); }


         $('#jqueryMessage').hide();

         var $spinnerid;
         var spinnerid = _getAttr(this, 'spinnerid');
         if (spinnerid) {
             $spinnerid = $('#' + spinnerid);
             $spinnerid.removeClass('hidden');
         }

         NODE = this;

         var param,
             data = $.extend(new Object(), $(this).data()),
             formData = $(this).hasClass('kss-form') ? '&' + $(this).closest('form').serialize() : '';
         for (var x=1; x<=4; x++) {
             param = _getAttr(NODE, 'param'+x);
             if (param) { data['param'+x] = param; }
         }
         var custom_param_str = _getAttr(this, 'custom');
         if (custom_param_str) {
             var custom_param_list = custom_param_str.split(/ +/);
             for (var i=0; i<custom_param_list.length; i++) {
                 var key_value = custom_param_list[i].split('-');
                 data[key_value[0]] = key_value[1]
             }
         }
         delete data['kss'];
         delete data['loading'];
         data = $.param(data, true) + formData;

         var url = _getURL($(this).data('kss') || _getAttr(this, 'url'));
         $.ajax({
           type: 'GET',
           url: url,
           data: data,
           headers: {'Kss': true},
           success: function(script) {
               //new Function(script)();
           },
           error: function(eventData) {
               _errorAjax(eventData);
           },
           complete: function() {
               cancelLoad();
               if ($load) { recoveryLoad($load_node, $load_default_content); }
               if ($spinnerid) { $spinnerid.addClass('hidden'); }
           }
         });

         if (!$(this).hasClass('KSSDefault')) event.preventDefault();
      });

    /* 默认表单提交模式 */
    $('body').on('click', 'form .submit input[type="submit"]', function(event) {
         if (/(kss|KSSFormSubmit)/.test($(this.form).attr('class'))) return;

         var $load_text = _getAttr(this, 'loading_text') || $(this).data('loading') || '...';
         $(this).after('<input type="button" value="' + $load_text + '" disabled="disabled" />');

         var $submitBtn = $(this).closest('form').find('input[type="submit"]');
         $submitBtn.hide();
         // 1.5秒后恢复
         win.setTimeout(function(){$submitBtn.show(); $submitBtn.next().remove();}, 1500)

         return true;
     });

    /* FormSubmit模式 */
    $('body').on('click', 'form.KSSFormSubmit input[type="submit"],' +
        'form.kss input[type="submit"], form.kss button[type="submit"]', function(event) {
         var $form = $(this.form);
         var $input = $form.find('#Submitted');
         if ($input.length) {
             $input.attr('name', this.name).val(this.value);
         } else {
             $form.append('<input id="Submitted" name="' + this.name + '" value="' + this.value + '" type="hidden" />');
         }
     });
    $('body').on('submit', 'form.KSSFormSubmit, form.kss', function(event) {
         // 是否有KSSLoad模式
         var $form = $(this);
         var $load_node = $form.find('[type="submit"]');
         if ($load_node.length > 1) {
             $load_node = $load_node.filter('[name="' + $form.find('#Submitted').attr('name') + '"]');
         }
         var $load = $load_node.hasClass('KSSLoad') || $form.hasClass('KSSLoad');
         var $load_text = '';
         var $load_default_content = getLoadDefaultContent($load_node);
         if ($load) {
             $load_text = _getAttr($load_node, 'loading_text') || $load_node.data('loading') || $form.data('loading') || '...';
             kssLoading($load_node, $load_text);
         }

         var $spinnerid;
         var spinnerid = _getAttr(this, 'spinnerid');
         if (spinnerid) {
             $spinnerid = $('#' + spinnerid);
             $spinnerid.removeClass('hidden');
         }
         $form.closest('.KSSFormArea').find('.KSSFormShowHide').toggleClass('hidden');

         $('#jqueryMessage').hide();

         // FIXME IE TinyMCE hack
         var iframe = $form.find('iframe');
         if (iframe.length !=0) {
             iframe.each(function(index) {
                 try {
                     var iframe_body = this.contentDocument.body;
                 } catch (e) {
                     /* IE6-7 */
                     var iframe_body = this.Document.body;
                 }
                 if (iframe_body.id == 'tinymce') {
                     $form.find('textarea#' + this.id.replace('_ifr', '')).text( iframe_body.innerHTML );
                 }
             });
         }

         NODE = this;
         var data = $form.serialize();
         var url = _getURL($form.attr('action'));
         $.ajax({
           type: 'POST',
           url: url,
           data: data,
           headers: {'Kss': true},
           success: function(script) {
               //new Function(script)();
           },
           error: function(eventData) {
               _errorAjax(eventData);
           },
           complete: function() {
               if ($load) { recoveryLoad($load_node, $load_default_content); }
               if ($spinnerid) { $spinnerid.addClass('hidden'); }
               $form.closest('.KSSFormArea').find('.KSSFormShowHide').toggleClass('hidden');
               $form.find('#Submitted').val('');
           }
         });
         if (!$(this).hasClass('KSSDefault')) event.preventDefault();
     });

    /* ShowHide模式 */
    $('body').on('click', '.KSSShowHideAction', function(event) {
         $(this).closest('.KSSShowHideArea').find('.KSSShowHideTarget').toggleClass('hidden');
         if (!$(this).hasClass('KSSDefault')) return false;
     });
    $('body').on('click', '.KSSShowHideAction2', function(event) {
         $(this).closest('.KSSShowHideArea2').find('.KSSShowHideTarget2').toggleClass('hidden');
         if (!$(this).hasClass('KSSDefault')) return false;
     });
    $('body').on('click', '.KSSShowHideAction3', function(event) {
         $(this).closest('.KSSShowHideArea3').find('.KSSShowHideTarget3').toggleClass('hidden');
         if (!$(this).hasClass('KSSDefault')) return false;
     });
    $('body').on('click', '.KSSShowHideAction4', function(event) {
         $(this).closest('.KSSShowHideArea4').find('.KSSShowHideTarget4').toggleClass('hidden');
         if (!$(this).hasClass('KSSDefault')) return false;
     });

    /* TabPage模式 */
    $('body').on('click', '.tabArea li a.node', function(event) {
        var tabArea = $(this).closest('.tabArea');

        $(this).closest('ul.tabs').find('li').removeClass('selected');
        $(this).closest('li').addClass('selected');

        tabArea.children('div.tabBody').addClass('hidden');
        var node = '#' + this.href.replace(/.*#/, '');
        var targetNode = tabArea.find(node);

        targetNode.removeClass('hidden');
        if ($(targetNode).hasClass('tabReset')) {
            $(targetNode).empty();
        }
        event.preventDefault();
     });

    $('body').on('click', 'div.KSSTabPageContentContainer .KSSCloseTab', function(event) {
        $('div.KSSTabPageContentContainer').empty();
     });

    /* Menu模式 */
    var isPop = false,
        isMsg = false;
    $('body').on('click', '.KSSActionMenu', function(event) {
         event.stopPropagation();
         $('.actionMenu').removeClass('relative');
         var menu = $(this).closest('.actionMenu');
         if (menu.css('display') != 'inline-block') { menu.addClass('relative'); }
         var currentMenuContent = menu.find('.KSSActionMenuContent');
         if (isMsg) {
             var messageMenuContent = $('#notify-center .KSSActionMenuContent');
             $('.KSSActionMenuContent').not(currentMenuContent).not(messageMenuContent).addClass('hidden');
             messageMenuContent.closest('.actionMenu').addClass('relative');
         } else {
             $('.KSSActionMenuContent').not(currentMenuContent).addClass('hidden');
         }
         currentMenuContent.toggleClass('hidden');
         if (!$(this).hasClass('KSSDefault')) return false;
         exitDialog();
     });
    $('html').on('click', function(e) {
         if($(win).data('bPopup')) isMsg = true;
         if (!isMsg) {
             $('.actionMenu').removeClass('relative');
             $('.KSSActionMenuContent').addClass('hidden');
         } else {
             var messageMenuContent = $('#notify-center .KSSActionMenuContent');
             $('.actionMenu').not(messageMenuContent.closest('.actionMenu')).removeClass('relative');
             $('.KSSActionMenuContent').not(messageMenuContent).addClass('hidden');
         }

         $('.JsDelete').remove();
         if (!isPop) try { exitDialog(); } catch (e) { /* 页面没完全加载 */ }
         else isPop = false;
     });
    $('body').on('click', '.popupDialog', function() { isPop = true; });
    $('#notify-center').hover(function() { isMsg = true; }, function(){ isMsg = false; });

     /* 禁止向上冒泡 */
    $('body').on('click', '.cancelBubble, .setTagsForm', function(event) {
         event.stopPropagation();
     });

    /* Close模式 */
    $('body').on('click', '.KSSCloseAction', function(event) {
         $(this).closest('.KSSCloseArea').addClass('hidden');
         $(this).closest('.KSSDeleteArea').remove();
         if (!$(this).hasClass('KSSDefault')) return false;
         // 禁止向上冒泡
         event.stopPropagation();
     })

    /* 全选与全不选模式(一) */
    $('body').on('click', '.KSSCheckArea .KSSCheckAll', function(event) {
         var node = $(this).closest('.KSSCheckArea');
         node.find('.KSSCheckItem').attr('checked', true);
         node.find('.KSSSelect').toggleClass('hidden');
         event.preventDefault();
     });
    $('body').on('click', '.KSSCheckArea .KSSUnCheckAll', function(event) {
         var node = $(this).closest('.KSSCheckArea');
         node.find('.KSSCheckItem').attr('checked', false);
         node.find('.KSSSelect').toggleClass('hidden');
         event.preventDefault();
     });

    /* 全选与全不选模式(二) */
    $('body').on('click', 'input.querySelect', function(event) {
        $(this).closest('.querySelectArea').find('input.chbitem').attr('checked', this.checked);
     });

    /* Drag Drop */
    $('body').on('mouseover', '.kss-draggable', function() {
         if ('uiDraggable' in $(this).data()) return;
         $(this).draggable({
           addClasses: false,
           containment: 'document',
           cursor: 'move',
           helper: 'clone',
           zIndex: 1000000,
           opacity: 0.35,
           create: function(event, ui) {
             $('.kss-droppable').each(function() {
               if ('uiDroppable' in $(this).data()) return;
               $(this).droppable({
                 addClasses: false,
                 hoverClass: 'ui-state-highlight',
                 drop: function(event, ui) {
                   var ths = $(this);
                     $.each(ui.draggable, function() {
                       ths.kss($(ths).data('drop'), $(this).data('drag'));
                     });
                 }
               });
             });
           }
         });
     });

    $('body').on('click', 'img.collapseFlag, img.expandFlag', function(event) {
        $(this).closest('.navTreeItem').toggleClass('collapsed').toggleClass('expanded');
        event.preventDefault();
        event.stopPropagation();
     });
    /* 导航树Ajax展开 */
    $('body').on('click', '.navtree img.loadTree, .navtree .toggleExpand', function(event) {
        event.preventDefault();
        event.stopPropagation();

        var $node = $(this).closest('li');
        var $nodeurl = $node.attr('kssattr:nodeurl');
        var $show_items = $node.attr('kssattr:show_items');
        var $include_all = $node.attr('kssattr:include_all');
        var $select_type = $node.attr('kssattr:select_type');

        if ($(this).hasClass('toggleExpand')) {
            var imgs = $node.find('img[onclick^=toggleChild]:lt(2)');
            imgs.toggleClass('hidden');
            if (!$nodeurl || imgs.length < 2 || $node.find('ul').length) {
                $node.find('ul:first').toggleClass('hidden');
                return;
            }
        }
        if ($nodeurl) {
            var $url = $nodeurl + '/@@show_child_tree';
        } else {
            var $url = $(this).parent().data('expand');
        }
        var $tree_generator = _getAttr(this, 'tree_generator');
        var $template = $(this).closest('div.navtree').attr('kssattr:templ');

        $(this).kss(
          $url, {
            template: $template,
            tree_generator: $tree_generator,
            show_items: $show_items,
            include_all: $include_all,
            select_type: $select_type}, 'GET'
        );
     });
    $('body').on('click', '.navtree li.navTreeItem a', function(event) {
        $(this).closest('.navtree').find('li.navTreeItem a').removeClass('navTreeCurrentItem').removeClass('selected');
        $(this).addClass('selected');
     });

    /* 选择组件'x'操作 */
    $('body').on('click', 'a.deselect', function(event) {
         event.preventDefault();
         // 权限面板上的人员从服务端返回删除
         if ($(this).closest('div.shareAuthorizeTable').length !=0) return;
         // 项目成员编辑上的人员从服务端返回删除
         if ($(this).closest('div.teamFiled').length !=0) return;

         var $parentNode = $(this).parent()
             ,$kss = $parentNode.closest('.select-field').children().last()
            ,value = $kss.data('value');
         if ($.isArray(value)) {
             var $uid = $parentNode.find('input').val()
               ,items = new Array();
             for (var i = 0; i < value.length; i++) {
                 if (value[i] != $uid) {
                     items.push(value[i]);
                 }
             }
             $kss.data('value', items);
         }
         $parentNode.remove();
     });

     $('body').on('click', 'a.profile_info', function(event) {
         var root_url = $('link[rel="root-url"]')[0].href;
         var id = $(this).attr('href').split('#')[1];
         var _base_url = root_url + '/desks/@@profile?pid='+id;
         if ($(this).hasClass('flash')) {
             if ($(this).hasClass('department')) {
                 var url = root_url + '/desks/@@change_department';
                 $(this).kss(url, {'pid':id});
                 // 修改tab标签
                 var a_link = $(this).closest('div.tabArea').find('ul.tabs').find('a');
                 for (var i=0; i<a_link.length; i++) {
                     $(a_link[i]).attr("kssattr:custom", $(a_link[i]).attr("kssattr:custom").replace(/pid-\w*(.\w*)*/, 'pid-'+id));
                 }
             } else {
                 win.open(_base_url, '_self');
             }
         } else {
             if (id.indexOf('users.') !== -1) {
               var url = root_url + '/desks/@@profileDialog';
               $(this).kss(url, {'pid':id, 'base_url': _base_url});
             } else {
               win.open(_base_url, '_self');
             }
         }
         event.preventDefault();
     });
 });

/*-----------------------------------------------------------------------------------------------------------*/

/* 每20秒钟后，自动删除portal-message提示 */
$('#portal-message').ready(function() {
     setInterval(function(){
         $('dl.portalMessage').remove()}, 20000)
 });

/* 绑定打印事件 */
$('#flash-viewer').unbind().bind('print', function() {
    $(this).kss({
      url: '@@printFile',
      params: {'uid': $(this).attr('uid')}
    });
 });

/* 根据 数据和模板 生成导航树 */
function render_navtree(data, template, load) {
     if (!(template instanceof Function)) return;

     var return_image = function(expanded, children) {
         if (children === null) return '';

         var cachePath = $('link[rel="cache-url"]').attr('href');
         if (expanded == true) {
             var img_html = '<img onclick="toggleChild(event, this)" src="' + cachePath + 'pl.gif" class="hidden">';
             img_html += '<img onclick="toggleChild(event, this)" src="' + cachePath + 'mi.gif">';
             return img_html;
         }
         else {
             var img_html = '<img onclick="toggleChild(event, this)" src="' + cachePath + 'pl.gif">';
             if (children === undefined) {
                 var img_html = '<img class="loadTree" onclick="toggleChild(event, this)" src="' + cachePath + 'pl.gif">';
             }
             img_html += '<img onclick="toggleChild(event, this)" src="' + cachePath + 'mi.gif" class="hidden">';
             return img_html;
         }
     }
     var return_attributes = function(classes, attr) {
         var attributes = '';
         if (classes) {
             attributes = ' class="' + classes + '"';
         }
         if (attr) {
             attributes += ' ' + attr;
         }
         return attributes;
     }
     var return_li_content = function(item) {
         var insert_img_htm = $(template(item)).prepend(return_image(item['expanded'], item['children']));
         if (insert_img_htm.length != 0) {
             var li_content = $('<div></div>').append(insert_img_htm.clone()).html();
         }
         else {
             var li_content = return_image(item['expanded'], item['children']) + template(item);
         }
         return li_content;
     }
     var return_child = function(expanded, data) {
         var html = '<ul class="navTreeLevel1 hidden">';
         if (expanded == true) {
             html = '<ul class="navTreeLevel1">';
         }
         if (data) {
             for (var x = 0; x < data.length; x++) {
                  var item = data[x];
                  html += '<li' + return_attributes(item['classes'], item['attributes']) + '>' + return_li_content(item);
                  html += return_child(item['expanded'], item['children']) + '</li>';
             }
             html += '</ul>';
             return  html;
         }
         else return '';
     }

     var html = '<ul class="navTreeLevel0">';
     if (load == true) {
         html = '<ul class="navTreeLevel1">';
     }
     for (var x = 0; x < data.length; x++) {
          var item = data[x];
          html += '<li' + return_attributes(item['classes'], item['attributes']) + '>' + return_li_content(item);
          html += return_child(item['expanded'], item['children']) + '</li>';
     }
     html += '</ul>';

     return html;
}

/*-----------------------------------------------------------------------------------------------------------*/

EDO.loaded = {}; // 已经加载的文件
EDO.templates = {}; // 已编译模板变量
function load(files, fnDone, fnFail) {
    if (!$.isArray(files)) { files = new Array(files); }
    if (!$.isFunction(fnDone)) { fnDone = new Function(); }
    if (!$.isFunction(fnFail)) { fnFail = new Function(); }

    var loadFiles = [],
        loadTemps = [],
        loadDicts = {},
        lang = $('html').attr('lang'),
        path = $('link[rel="root-url"]').attr('href') + '/@@',
        cachePath = $('link[rel="cache-url"]').attr('href'),
        isCache = !/\/@@\/$/.test(cachePath),
        linkReg = /^https?/i,
        handlebarReg = /.hb$/i,
        CSSReg = /.css$/i,
        javaScriptReg = /.js$/i,
        i18njavaScriptReg = /.i18n.js/i,
        loaded = EDO.loaded,
        templates = EDO.templates;

    for (var x = 0; x < files.length; x++) {
         var url, file = files[x];
         if (!loaded[file] && $.inArray(file, loadFiles) == -1) {
             if (javaScriptReg.test(file)) {
                 if (i18njavaScriptReg.test(file)) {
                     if (isCache) {
                         url = cachePath + 'i18njs/' + lang + '/' + file;
                     } else {
                         url = path + file;
                     }
                 } else if (linkReg.test(file)) {
                     url = file;
                 } else {
                     url = cachePath + file;
                 }
                 loadFiles.push(url);
                 loadDicts[url] = file;
             } else if (CSSReg.test(file)) {
                 var href = linkReg.test(file) ? file : cachePath + file;
                 $('head').append('<link media="all" href="' + href + '" rel="stylesheet" type="text/css">');
                 loaded[file] = true;
             } else if (handlebarReg.test(file)) {
                 if (isCache) {
                     url = cachePath + 'hb/' + lang + '/' + file + '.js';
                     loadFiles.push(url);
                 } else {
                     url = path + file;
                     loadTemps.push(url);
                 }
                 loadDicts[url] = file;
             }
         }
    }
    var fnLoadFiles = function() {
        if (!loadFiles.length) {
            fnDone.apply();
        } else {
            $LAB
              .setGlobalDefaults({'ErrorHandler': fnFail})
              .script(loadFiles)
              .wait(function() {
                  $.each(loadFiles, function() { loaded[loadDicts[this]] = true; });
                  fnDone.apply();
              });
        }
    };
    if (loadTemps.length) {
        var success = function(data) {
            var filename = loadDicts[this.url];
            var templname = filename.replace(handlebarReg, '');
            templates[templname] = Handlebars.compile(data);
            loaded[filename] = true;
        }
        var deferreds = $.map(loadTemps, function(current) {
            var ajaxOptions = {url:current, success:success, dataType:'html', cache:true};
            return $.ajax(ajaxOptions);

        });
        $.when.apply($, deferreds).then(function() {
            fnLoadFiles();
        }, function() {
            fnFail.apply();
        });
    } else { fnLoadFiles(); }
}

/*-----------------------------------------------------------------------------------------------------------*/

/* 修复IE6/7/8中不支持 toISOString 方法 */
if (!Date.prototype.toISOString) {
    Date.prototype.toISOString = function() {
        function pad(n) { return n < 10 ? '0' + n : n }
        return this.getUTCFullYear() + '-'
            + pad(this.getUTCMonth() + 1) + '-'
            + pad(this.getUTCDate()) + 'T'
            + pad(this.getUTCHours()) + ':'
            + pad(this.getUTCMinutes()) + ':'
            + pad(this.getUTCSeconds()) + '.'
            + pad(this.getUTCMilliseconds()) + 'Z';
    }
}
