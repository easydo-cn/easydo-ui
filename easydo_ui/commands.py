# -*- encoding:utf-8 -*-
import json
import urllib
from types import StringTypes

class JqueryMixin:

    def _escape_value(self, value):
        if not value:
            return "''"
        if not isinstance(value, basestring):
            value = value.html()
        value = value.replace('\\', '\\\\').replace('\'', '\\\'').replace('\n', r'\n').replace('\r', r'\r')
        value = value.replace('</script>', "</' + 'script>")
        return "'%s'" % value

    def empty(self):
        self._append_script("empty()")

    def focus(self):
        self._append_script("focus()")

    def blur(self):
        self._append_script("blur()")

    def remove(self):
        self._append_script("remove()")

    def add_class(self, value):
        self._append_script("addClass('%s')" % value)

    def remove_class(self, value):
        self._append_script("removeClass('%s')" % value)

    def toggle_class(self, value):
        self._append_script("toggleClass('%s')" % value)

    def attr(self, name, value):
        value = json.dumps(value)
        self._append_script("attr('%s', %s)" % (name, value))

    def data(self, name, value):
        value = json.dumps(value)
        self._append_script("data('%s', %s)" % (name, value))

    def val(self, value):
        self._append_script("val('%s')" % value)

    def css(self, name, value):
        self._append_script("css('%s', '%s')" % (name, value))

    def set_content(self, value='', js_var=None):
        selector = self._selector or '$(NODE)'
        if selector == "$('#content')":
            self.replaceContent(value)
            return

        if js_var is not None:
            value = js_var
        else:
            value = self._escape_value(value)
        self._append_script("%s.trigger('destroyed').find('.kss-com').trigger('destroyed')" % selector, False, False)
        self._append_script("html(%s)" % value)
        if self.request.is_mobile():
            self._append_script("mobile()", False)

    def replace(self, value='', js_var=None):
        if js_var is not None:
            value = js_var
        else:
            value = self._escape_value(value)

        self._append_script("%s.find('.kss-com').trigger('destroyed')" % (self._selector or '$(NODE)'), False, False)
        self._append_script("replaceWith(%s)" % value)

    def append(self, value):
        self._append_script("append(%s)" % self._escape_value(value))

    def prepend(self, value):
        self._append_script("prepend(%s)" % self._escape_value(value))

    def after(self, value):
        self._append_script("after(%s)" % self._escape_value(value))

    def before(self, value):
        self._append_script("before(%s)" % self._escape_value(value))

    def on(self, event, kss, conditions={}):
        if event == 'idle':
            self._append_script("onIdle('%s')" % kss, False)
        else:
            data = json.dumps({'kss': kss})
            if not self._selector or self._selector == '$(NODE)':
                self._selector = "$(document)"
            self._append_script("ksson('%s', %s, %s)" % (event, data, conditions))

    def off(self, event, kss=''):
        if event == 'idle':
            self._append_script("offIdle('%s')" % kss, False)
        else:
            self._append_script("off('%s', '%s')" % (event, kss), False)

    def trigger(self, event, data={}):
        data = json.dumps(data)
        if not self._selector or self._selector == '$(NODE)':
            self._selector = "$(document)"
        self._append_script("trigger('%s', %s)" % (event, data))

    def sound(self, typ='info'):
        self._append_script("sound('%s')" % typ, False)

class SelectorMixin:
    components = {}

    @staticmethod
    def register_component(kss_component):
        SelectorMixin.components[kss_component.name] = kss_component

    def _build_selector(self, selector, cmd):
        if not isinstance(selector, StringTypes):
            self._selector = selector(self)._selector
            return self

        _selector = selector
        component = self
        # 组件？
        for name, _component in self.components.items():
            if _selector.startswith(name):
                _selector = _component.selector + _selector[len(name):]
                component = _component(self)
                break

        if not self._selector:
            if cmd:
                self._selector = "$(NODE).%s('%s')" % (cmd, _selector)
            else:
                self._selector = "$('%s')" % _selector
        else:
            self._selector += ".%s('%s')" % (cmd, _selector)

        # 组件？
        return component

    def parent(self):
        if not self._selector:
            self._selector = '$(NODE).parent()'
        else:
            self._selector += '.parent()'
        return self

    def prev(self):
        if not self._selector:
            self._selector = '$(NODE).prev()'
        else:
            self._selector += '.prev()'
        return self

    def select(self, selector):
        return self._build_selector(selector, '')

    def closest(self, selector):
        return self._build_selector(selector, 'closest')

    def find(self, selector):
        return self._build_selector(selector, 'find')

    def children(self, selector):
        return self._build_selector(selector, 'children')

    def filter(self, selector):
        return self._build_selector(selector, 'filter')

    def exclude(self, selector):
        return self._build_selector(selector, 'not')

class EDOMixin:

    skin_name = ''

    def active(self):
        self.add_class("active")

    def use_skin(self, skin_name):
        self.skin_name = skin_name

    def message(self, text, typ='info'):
        text = self._escape_value(text)
        if typ == 'float':
            self._append_script("message_float(%s)" % text, False)
        else:
            if typ =='error': typ = 'mserror'
            self._append_script("$().message(%s, '%s')" % (text, typ), False)

    def set_cookie(self, name, value, expires=36500, path='/'):
        self._append_script("$.cookie('%s', '%s', {expires:%s, path:'%s'})" % (name, value, expires, path), False)

    def remove_cookie(self, name, path='/'):
        self._append_script("$.removeCookie('%s', {path:'%s'})" % (name, path), False)

    def redirect(self, url):
        self._append_script("window.location.href='%s'" % url, False)

    def open_window(self, url):
        self._append_script("window.open('%s')" % url, False)

    def load(self, files, scripts=None):
        if scripts == None:
            self._scripts.append('"use load";')
            self._files.extend(files)
        else:
            if isinstance(scripts, list):
                scripts = '\n'.join(scripts)

            script = 'load(%s, function(){%s})' % (files, scripts)
            self._append_script(script, False)
            return script

    def modal(self, html='', focus=True, fixed=False, width=600):
        fixed = fixed and 'true' or 'false'
        focus = focus and 'true' or 'false'
        if not isinstance(html, basestring):
            html = html.html()

        el = 'bPopup-%s' % id(self)
        html = '<div id="%s" class="popup-container %s kss-com" width="%s" height="%s"><a class="modalCloseImg b-close" title="Close"></a> \
        <div class="simplemodal-wrap">%s</div></div>' % (el, el, width, 450, html)
        script = '''$(%s).bPopup({
          modalClose:false,
          follow:[%s,%s],
          opacity:0.5,
          closeClass:"b-close",
          position:['auto','auto'],
          focus: %s})''' % (self._escape_value(html), fixed, fixed, focus)

        self._append_script(script, False)
        if self.request.is_mobile():
            self._append_script("mobile()", False)

    def replace_modal(self, value):
        if not isinstance(value, basestring):
            value = value.html()
        self.select('.popup-container:last').find('.simplemodal-wrap').set_content(value)

    def active_modal(self):
        self.select('.popup-container:last')
        return self

    def close_modal(self, all=False):
        all = all and 'true' or 'false'
        self._append_script("closeModal(%s)" % all, False)

    def set_batch_actions(self, html=''):
        html = '''
        <div style="width: 100%%; height: 105px; background: #E0EBF6; border-bottom: 1px solid #DCE8F5; width: 100%%;" id="actionsPop">
            <div style="margin-top: 48px; text-align:center;" class="batchActions">
                %s
                <button class="actions-close button danger active" i18n:translate="cancel">取消</button>
            </div>
        </div>
        ''' % html

        script = '''
            $(%s).bPopup({
                closeClass: 'actions-close',
                position: [0, 0],
                escClose: false,
                positionStyle: 'fixed',
                modal: false,
                zIndex: 4000,
                focus: false,
                onClose: function() {
                    $('#actionsPop').remove();
                    $('#content .chbactions').attr('checked', false);
                },
                onOpen: function() {
                    $(window).data('bPopup', null);
                }
            })
        ''' % self._escape_value(html)
        self._append_script(script, False)

    def close_batch_actions(self):
        self._append_script('closeActions()', False)

    def compile_template(self, template_name, template_body):
        script = "if(!EDO.templates['%s']){EDO.templates['%s'] = Handlebars.compile(%s);}" % \
            (template_name, template_name, self._escape_value(template_body))
        self._append_script(script, False)

    def render_template(self, template_name, template_var, data):
        script = "var %s = EDO.templates['%s'](%s)" % (template_var, template_name, json.dumps(data))
        self._append_script(script, False)

    def goTop(self):
        self._append_script("document.documentElement.scrollTop=0", False)

    def replaceContent(self, value):
        value = self._escape_value('<div id="content">%s</div>' % value)
        self._append_script('''
            $('#content .kss-com').trigger('destroyed');
            try {
                var confirm_msg=window.onbeforeunload();
            } catch(e) {
                var confirm_msg;
            }
            if (confirm_msg) {
                if (window.confirm(confirm_msg)) {
                    UnloadConfirm.clear();
                    $('#content').replaceWith(%s);
                    closeActions();
                    $(window).resize();
                }
            } else {
                $('#content').replaceWith(%s);
                closeActions();
                $(window).resize();
            }''' % (value, value), False)

    def setTimeout(self, script, millisec=500):
        self._append_script("setTimeout(%s, %s)" % (self._escape_value(script), millisec), False)

    def actionShowHide(self):
        self.closest('.KSSShowHideArea').find('.KSSShowHideTarget').toggle_class('hidden')

    def closeTabPage(self):
        self.closest('.KSSTabArea').find('.KSSDeleteArea').remove()

    def closeContentForm(self):
        self.select('#content, #right .portlet, #above-content-bar').remove_class('hidden')
        self.closest('#kss-content-form').remove()
        self.select('.KSSContentFormAction').find('.KSSTabPlain').remove_class('hidden')
        self.select('.KSSContentFormAction .KSSTabSelected').add_class('hidden')

    def showTabPage(self, value, width='800px', title=''):
        from zopen.skin.macros import PopupDialogMacro
        content = PopupDialogMacro(self.context, self.request, title=title, banner='', body=value, width=width).render()
        content = self._escape_value(content)

        self._append_script("var tabContent=$(NODE).closest('.KSSTabArea').find('.KSSTabPageContentContainer')", False)
        self._append_script("tabContent.html(%s)" % content, False)
        self._append_script("if($('#right').is(':hidden') && $(NODE).closest('.contentbar_right').length){$('.KSSTabPageContentContainer div.popupDialog').css('right','2%')}", False)

        if not title:
            self._append_script("tabContent.find('.popupDialogHeaderLeft').text($(NODE).text())", False)

    def showContentForm(self, value):
        content = """<div id="kss-content-form">%s</div>""" % value
        self.select('#kss-content-form').remove()
        self.select('#kss-spinner, #content').add_class('hidden')
        self.select('#content').after(content)

    def disable_kss(self):
        self.remove_class('kss')

    def push_state(self, request, title, url=''):
        if request.is_mobile():
            # FIXME hack在微信等webview中无法修改document.title的情况
            script = '''
                (function(){
                    var $body = $('body');
                    var $iframe = $('<iframe src="/@@/img/favicon.ico" style="display:none;"></iframe>').on('load', function() {
                        setTimeout(function() {
                            $iframe.off('load').remove()
                        }, 0)
                    }).appendTo($body);
                })();
            '''
            self._append_script(script, False)

        title = self._escape_value(title)
        # 不是ajax请求不pushState
        if not request.headers.has_key('kss'):
            self._append_script('document.title=%s' % title, False)
            return

        form = self.request.form
        # 是否是回退
        if form.has_key('back'):
            return
        else:
            form['back'] = True

        kss = request.getURL()
        if form:
            kss += '?%s' % urllib.urlencode(form)

        data = json.dumps({'form':form, 'url':kss})
        if not url:
            url = urllib.unquote(kss)

        script = "History.trigger=false;History.pushState(%s, %s, '%s')" % (data, title, url)
        self._append_script(script, False)

    def kss(self, url):
        self._append_script("kss('%s')" % url)

    def set_idle(self, second, timeout=0):
        self._append_script('EDO.idle=%s;EDO.idleTimeout=%s' % (second, timeout), False)
        return self

class Commands(JqueryMixin, SelectorMixin, EDOMixin):

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self._files = []
        self._scripts = []
        self._selector = ""

    def _append_script(self, script, query=True, clear=True):
        script = script if script.endswith(';') else ('%s;' % script)
        if query:
            if not self._selector:
                self._selector = "$(NODE)"

            script = '%s.%s' % (self._selector, script)
            self._scripts.append(script)
        else:
            self._scripts.append(script)

        if clear:
            self._selector = ""

    def append_script(self, script):
        self._append_script(script, False, False)

    def clear(self):
        self._append_script("val('')")

    def javascript(self):
        # load 模式
        if '"use load";' in self._scripts:
            return self.load(self._files, self._scripts)
        else:
            return '\n'.join(self._scripts)


