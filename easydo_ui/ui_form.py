# encoding: utf-8
import cgi
import json
import random
from string import Template
from datetime import datetime
from utils import get_address
from zopen.apps.adapters import json2field
from zopen.edo.oc.operator.utils import getRoot
from zopen.team.utils import get_teamaware
from zopen.personselector.selected import SelectedProvider
from zopen.filerepos.browser.folder.macros import FolderSelectMacro
from zopen.upload.macros import FolderBrowserMacro, FileSelectMacro, MacroFlashUploadField
from zopen.versionedresource.patch import versionedURL
from zopen.flow.browser.macros import DataItemSelectMacro, FlowSelectMacro
from zopen.tags.macros import TagFieldMacro
from zopen.utils.environ import getRequest
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.app.pagetemplate import ViewPageTemplateFile
from ._base import BaseUI, Element, KssCommands, BaseKss

from zope.i18n import translate
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('easydo')

REQUIRED_HTML = '<img src="/@@/img/required.gif" style="padding-left:2px" title="必填"/>'

class form(Element):
    _layout = 'table'
    _template = ''
    form_def = None
    title = description = ''
    omit_fields = ()

    def __init__(self, form_def=None, action='', title=None, description=None, klass=''):
        self.action = action
        self._set_form_def(form_def)
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self._buttons= []
        self.loading_text = '...'
        self.hidden_input = ''
        self._triggers = {}
        self._widgets = []
        self.fields() # init data
        self.klass = list(self._klass)
        if klass:
            self.klass.append(klass)

    def _set_form_def(self, form_def=None):
        if form_def is None: return
        self.form_def = form_def
        self.title = self.title or getattr(form_def, 'title', '')
        self.description = self.description or getattr(form_def, 'description', '')

    def fields(self, form_def=None, data={}, template=None, edit_fields=None, omit_fields=(), errors={}, **options):
        self._set_form_def(form_def)
        self.data = data
        self._template = template
        self.edit_fields = edit_fields
        self.omit_fields = omit_fields
        self.errors = errors
        self.options = options
        return self

    def hidden(self, data):
        for key, value in data.items():
            self.add(hidden_input(key, value))
        return self

    def layout(self, layout='table'):
        self._layout = layout
        if layout == 'inline':
            self._template = self._gen_inline_layout()
        elif layout == 'div':
            self._template = self._gen_div_layout()
        else:
            self._template = self._gen_table_layout()
        return self

    def template(self, template):
        self._template = template
        return self

    def button(self, name, title, style='default'):
        self._buttons.append((name, title, style))
        return self

    def kss(self, url):
        self.on('submit', url)
        return self

    def loading(self, text):
        self.loading_text = text
        return self

    def add(self, widget):
        self._widgets.append(widget)
        return self

    def _gen_inline_layout(self, omitted_fields=[]):
        """生成一个紧凑型的表单模版"""
        field_rows = []
        for field in self._widgets:
            if field.name not in omitted_fields and isinstance(field, FormInput)\
                    and not isinstance(field, hidden_input):
                field_rows.append("<th>%s：</th><td>$%s</td>" % \
                       (field.title + (field.required and REQUIRED_HTML or ''), field.name))
        if field_rows:
            return '<table class="vertical listing"><tr>%s</tr></table>' % (''.join(field_rows))
        else:
            return ''

    def _gen_table_layout(self, omitted_fields=[]):
        """生成一个紧凑型的表单模版"""
        field_rows = []
        for field in self._widgets:
            if field.name not in omitted_fields and isinstance(field, FormInput)\
                    and not isinstance(field, hidden_input):
                field_rows.append("<tr><th>%s：</th><td>$%s</td></tr>" % \
                       (field.title + (field.required and REQUIRED_HTML or ''), field.name))
        if field_rows:
            return '<table class="vertical listing">%s</table>' % (''.join(field_rows))
        else:
            return ''

    def _gen_div_layout(self, omitted_fields=[]):
        """生成一个松散型的表单模版"""
        result = []
        for field in self._widgets:
            if field.name not in omitted_fields and isinstance(field, FormInput)\
                    and not isinstance(field, hidden_input):
                label = field.title + (field.required and REQUIRED_HTML or '')
                if field.description:
                   result.append('<div><div class="field"><label>%s</label><p class="formHelp">%s</p>$%s</div></div>' % (label, field.description, field.name))
                else:
                   result.append('<div><div class="field"><label>%s</label><br />$%s</div></div>' % (label, field.name))
        return ''.join(result)

    def _gen_buttons_html(self, actions):
        if not actions: return ''
        action_htmls = ['<input type="hidden" name="form.submitted" value="1" />']
        for name, title, style in actions:
            style = {'error':'danger', 'primary':'active'}.get(style, style)
            if name == '_save.0' and len(actions) > 1:
                action_htmls.append(u'<input style="float:right" type="submit" class="submit button %s" name="form.button.%s" value="%s" />' % (style, name, title))
            else:
                action_htmls.append(u'<input type="submit" class="submit button %s" name="form.button.%s" value="%s" />' % (style, name, title))
        return ''.join(action_htmls)

    def html(self):
        # 不推荐的旧的方式
        form_html = ''
        if self.form_def is not None:
            form_html = self.form_def.render(self.data, self._template, self.edit_fields, self.omit_fields, self.errors, **self.options)
            for widget in self._widgets:
                form_html += widget.html()
            buttons = self.form_def.buttons(self._buttons)

        else:
            fields_html = {}
            for widget in self._widgets:
                if isinstance(widget, hidden_input):
                    form_html += widget.html()
                else:
                    fields_html[widget.name] = widget.html()
            if not self._template: self.layout()
            form_html += Template(self._template).safe_substitute(fields_html)
            buttons = self._gen_buttons_html(self._buttons)

        if 'submit' in self._triggers:
            kss_url = self._triggers['submit'][0][0]
        else:
            kss_url = ''

        klass = ' '.join(self.klass)
        if kss_url:
            klass += ' KSSLoad'
            loading_data = 'data-loading="%s"' % self.loading_text
        else:
            loading_data = ''

        desc, h3 = '', ''
        if self.title: h3 = '<h3>%s</h3>' % self.title
        if self.description: desc = '<div class="discreet m_b_3">%s</div>' % self.description
        if self._layout == 'inline':
            return '''<form action="%s" %s class="%s" method="post">%s%s<table style="width: 100%%"><tr><td>%s</td><td>%s</td></tr></table>%s</form>''' % \
                (kss_url or self.action, loading_data, klass, h3, desc, form_html, buttons, self.hidden_input)
        else:
            return '''<form action="%s" %s class="%s" method="post">%s%s%s%s%s</form>''' % \
                    (kss_url or self.action, loading_data, klass, h3, desc, form_html, buttons, self.hidden_input)

    def get_submitted(self, request_form, check_required=True, keep_multiple=True):
        """ 返回 button, errors, result """
        if self.form_def is not None:
            button = self.form_def.get_button(None, request_form)
            fields = set(self.form_def.keys()) - set(self.omit_fields)
            errors, result = self.form_def.submit(request_form, fields=fields, check_required=check_required, keep_multiple=keep_multiple, **self.options)
            return button, errors, result

        button = ''
        for key in request_form:
            if key.startswith('form.button.'):
                button = key[len('form.button.'):]
                break
        if not button: return '', {}, {}

        # 逐一校验，保存
        errors, result = {}, {}
        for field in self._widgets:
            if field.readonly: continue

            if not request_form.has_key(field.name):
                if check_required and field.required:
                    errors[field.name] = '必须填写 %s' % field.title
                    continue

                if hasattr(field, 'empty_value'):  # 空值处理
                    field_value = field.empty_value
                else:
                    continue
            else:
                field_value = request_form.get(field.name)

            if check_required and field.required and not field_value:
                errors[field.name] = '必须填写 %s' % field.title
                continue

            result[field.name] = field_value

        return button, errors, result

class field(BaseUI):

    def __init__(self, **kw):
        self._field, fields = json2field(kw)
        if fields:
            self._field.add_fields(fields)

        self._value = None
        self.options = {}

    def value(self, value, **options):
        self._value = value
        self.options = options
        return self

    def html(self):
        return self._field.render_input(self._value, **self.options)

def _gen_on_js(self, event):
    items = self._triggers.get(event, [])
    if items:
        url = items[0][0]
        if "?" in url:
            return "$(this).kss('%s&value=' + this.value)" % url
        else:
            return "$(this).kss('%s?value=' + this.value)" % url
    else:
        return ''

class FormInput(Element):
    multiple = True

    def __init__(self, name, value='', title='', description='', required=False, readonly=False, placeholder='', **kw):
        Element.__init__(self, **kw)
        self.name = name
        self.title = title
        self.description  = description
        self.required = required
        self.placeholder = placeholder
        self.value = value
        self.readonly = readonly

    def _get_attr(self):
        attr = self.attr.items()
        if self.id:
            attr.append(('id', self.id))
        attr.append(('name', self.name))
        attr.append(('class', ' '.join(self.klass)))
        attr.append(('onchange', _gen_on_js(self, 'change')))
        attr.append(('onblur', _gen_on_js(self, 'blur')))
        return ' '.join(['%s="%s"' % (name, cgi.escape(str(value), True)) for (name, value) in attr if value])

    def _get_data(self):
        return ' '.join(['data-%s="%s"' % (name, cgi.escape(value, True)) for (name, value) in self.data.items() if value])

class hidden_input(FormInput):

    def html(self):
        if not isinstance(self.value, (str, unicode)):
            self.value = json.dumps(self.value)
        return '<input type="hidden" name="%s" value="%s" />' % (self.name, cgi.escape(self.value, True))

class text_line(FormInput):
    _icon = ''
    _type = 'text'

    def icon(self, icon):
        self._icon = icon
        return self

    def html(self):
        value = cgi.escape(self.value, True)
        if self.readonly: return value

        self.klass.extend(['text-line', 'controls'])
        self.attr['type'] = self._type
        self.attr['placeholder'] = self.placeholder
        self.attr['value'] = value

        attr = self._get_attr()
        data = self._get_data()

        result = '<input style="100%%" %s %s />' % (attr, data)
        if self._icon:
            return '<div class="input-prepend"><span class="add-on"><i class="fa fa-%s"></i></span> %s </div>' % (self._icon, result)
        else:
            return result

class password(text_line):
    _type = 'password'

class KssTextLine(BaseKss):
    name = 'text-line'
    selector = '.text-line'

    def set_value(self, value):
        self.kss.val(value)

KssCommands.register_component(KssTextLine)

def _gen_select_options(options, value):
    html = ''
    for item in options:
        if isinstance(item, (str, unicode)):
            key, _value = item, item
        elif isinstance(item, (tuple, list)):
            key, _value = item

        if isinstance(_value, (tuple, list)):
            html += '<optgroup label="%s">' % key
            html += _gen_select_options(_value, value)
            html += '</optgroup>'
        else:
            if key in value:
                html += '<option selected="selected" value="%s">%s</option>' % (key, _value)
            else:
                html += '<option value="%s">%s</option>' % (key, _value)
    return html

class basic_select(FormInput):
    el = 'select'
    multiple=False

    def __init__(self, name, options='', multiple=None, **kw):
        FormInput.__init__(self, name, **kw)
        if multiple is not None:
            self.multiple = multiple
        self.options = options

    def html(self):
        value = cgi.escape(self.value, True)
        if self.readonly: return value

        self.klass.extend(['controls', self.__class__.__name__])

        attr = self._get_attr()
        data = self._get_data()
        return '<select %s %s>%s</select>' % (attr, data, _gen_select_options(self.options, self.value))

class KssSelect(BaseKss):
    name = 'basic_select'
    selector = '.basic_select'

    def set_value(self, value):
        self.kss.val(value)

    def set_options(self, options):
        html = _gen_select_options(options, '')
        self.kss.set_content(html)

KssCommands.register_component(KssSelect)

class select2(basic_select):

    def html(self):
        return basic_select.html(self) + '''
            <script type="text/javascript">
                load(['select2/select2.js', 'select2/select2_locale_zh-CN.js', 'select2/select2.css'], function(){
                  $('select.select2').css('width', '97.5%').select2();
                });
             </script>'''

class radio_select(basic_select):

    def __init__(self, name, inline=False, **kw):
        basic_select.__init__(self, name, **kw)
        self.inline = inline

    def html(self):
        attr = self._get_attr()
        data = self._get_data()

        _html = ''
        br = '' if self.inline else '<br />'
        for key, _value in self.options:
            checked = key == self.value and 'checked="checked"' or ''
            _html +='<input type="radio" name="%s" %s value="%s" id="for_field_%s" %s %s /><label for="for_field_%s">%s</label> %s' % (self.name, checked, key, key, attr, data, key, _value, br)
        return _html

class check_select(radio_select):
    multiple=True

    def html(self):
        attr = self._get_attr()
        data = self._get_data()

        _html = ''
        br = '' if self.inline else '<br />'
        for key,value in self.options:
            checked = key in self.value and 'checked="checked"' or ''
            _html +='<input type="checkbox" %s name="%s" value="%s" %s %s id="for_multi_field_%s"/><label for="for_multi_field_%s">%s</label> %s' % (checked, self.name, key, attr, data, value,  value, value, br)
        return _html

class text_area(FormInput):

    def __init__(self, name, rows=3, **kw):
        FormInput.__init__(self, name, **kw)
        self.rows = rows

    def html(self):
        value = cgi.escape(self.value)
        if self.readonly: return value

        self.attr['rows'] = self.rows

        attr = self._get_attr()
        data = self._get_data()
        return '<textarea %s %s>%s</textarea>' % (attr, data, value)

class rich_text(FormInput):

    def __init__(self, name, rows=3, **kw):
        FormInput.__init__(self, name, **kw)
        self.rows = rows

    def html(self):
        if self.readonly: return self.value

        self.attr['rows'] = self.rows
        self.klass.append('mini-mceEditor')

        attr = self._get_attr()
        data = self._get_data()
        return '''
            <textarea %s %s>%s</textarea>
            <script type="text/javascript">$(function(){initTinyMCE();});</script>
        ''' % (attr, data, self.value)

class ace(FormInput):

    def __init__(self, name, mode='python', width=900, height=450, **kw):
        FormInput.__init__(self, name, **kw)
        self.width = width
        self.height = height
        self.mode = mode

    def html(self):
        value = cgi.escape(self.value)
        if self.readonly: return value

        aceid = self.id or 'form-widgets-%d' % random.randrange(0, 9999)

        html = '''
            <div id="%(aceid)s" class="%(klass)s" style="width: %(width)s;height: %(height)spx;display: none;">%(value)s</div>
            <textarea name="%(name)s" class="hidden">%(value)s</textarea>

            <script type="text/javascript">
                load(['ace/src/ace.js', 'ace/src/mode-%(mode)s.js'], function(){
                    ace.config.set('basePath', '%(path)s');
                    var editor = ace.edit("%(aceid)s");
                    editor.setTheme("ace/theme/github");
                    var Mode = require("ace/mode/%(mode)s").Mode;
                    editor.getSession().setMode(new Mode());
                    editor.setFontSize(14);
                    editor.on("change", function(e){
                        $('#%(aceid)s').next().val(editor.getValue());
                    });
                    $('#%(aceid)s').show();
                });
            </script>
        ''' % {
            'aceid': aceid,
            'name': self.name,
            'klass': ' '.join(self.klass),
            'width': self.width,
            'height': self.height,
            'value': value,
            'mode': self.mode,
            'path': versionedURL('ace/src'),
        }
        return html

class nav_select(FormInput):

    def __init__(self, name='filter_type', title='', value='Content', options=[], **kw):
        request = getRequest()
        if not title:
            title = translate(_('Filter'), context=request)
        if not options:
            options = [
                ('Content', translate(_('All Content'), context=request)),
                ('DataItem', translate(_('DataItem'), context=request)),
                ('File', translate(_('all_files', 'All Files'), context=request)),
                ('office', translate(_('office', 'Office Documents'), context=request)),
                ('text', translate(_('txt_code', 'Text'), context=request)),
                ('image', translate(_('images', 'Images'), context=request)),
                ('compress', translate(_('RAR', 'Compressed'), context=request)),
                ('media',  translate(_('audio_video', 'Media'), context=request)),
            ]
        FormInput.__init__(self, name, title=title, value=value, **kw)
        self.options = options

    def html(self):
        content = '''<div style="padding-left: 5px;" class="filter_type">
                <input type="hidden" name="%s" />
        ''' % self.name
        for name, title in self.options:
            if name == self.value:
                classes = 'discreet selected'
            else:
                classes = 'discreet'

            onclick = '$(this).parent().find(&quot;input&quot;).val(&quot;%s&quot;);$(this).closest(&quot;form&quot;).submit();' % name
            link = '<a data-type="%s" style="margin-right: 10px;" href="javascript:;" class="%s" onclick="%s">%s</a>' % \
                (name, classes, onclick, title)
            content += link
        content += '</div>'
        return content

class date_time(FormInput):

    def __init__(self, name, showtime=True, minutestep=30, **kw):
        FormInput.__init__(self, name, **kw)
        self.showtime = showtime
        self.minutestep = minutestep

    def html(self):
        if isinstance(self.value, datetime):
            if self.showtime:
                value = self.value.strftime('%Y-%m-%d %H:%M')
            else:
                value = self.value.strftime('%Y-%m-%d')
        elif self.value is None or self.value == '':
            value = ''

        onchange = _gen_on_js(self, 'change')
        html = """<input class="PopCalendar" kssattr:showtime="%s" kssattr:minutestep="%d" type="text"
                  name="%s" value="%s" onchange="%s" size="%s" />"""  % \
                (self.showtime and 'true' or 'false', self.minutestep, self.name, value, onchange, 16 if self.showtime else 10)
        return html

class tag_select(FormInput):

    def __init__(self, name, context, request, **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request

    def html(self):
        return TagFieldMacro(self.context, self.request, \
                value=self.value, name=self.name).render()

class person_select(FormInput):

    def __init__(self, name, context, request, multiple=False, object_types=['person', 'group'],  **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request
        self.multiple = multiple
        self.object_types = object_types

    def html(self):
        onchange = _gen_on_js(self, 'change')

        # FIXME 大部分时候会找两遍
        context = get_teamaware(self.context) or getRoot(self.context)
        selectedProvider = SelectedProvider(context, self.request, view=None)

        selectedProvider.multiple_selection = self.multiple
        selectedProvider.onchange = onchange
        selectedProvider.name = self.name

        if self.value:
            if isinstance(self.value, basestring):
                selectedProvider.selected_members = (self.value,)
            else:
                selectedProvider.selected_members = self.value
        if 'person' in self.object_types and 'group' in self.object_types:
            selectedProvider.group_or_person = 'persongroup'
        elif 'person' in self.object_types:
            selectedProvider.group_or_person = 'persononly'
        else:
            selectedProvider.group_or_person = 'grouponly'
        selectedProvider.update()
        return '<div class="personField">%s</div>' % selectedProvider.render()


class folder_select(FormInput):

    def __init__(self, name, context, request, multiple=False, **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request
        self.multiple = multiple

    def html(self):
        return FolderSelectMacro(self.context, self.request,
                        value=self.value, name=self.name, multiple=self.multiple).render()

class location_select(FormInput):

    def __init__(self, name, context, request, **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request

    def html(self):
        return FolderBrowserMacro(self.context, self.request, self.name, '', select_all=True).render()

class file_upload(FormInput):

    def __init__(self, name, context, request, **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request

    def html(self):
        html_id = self.name.split(':', 2)[0].replace('.', '_')
        macro_flash_upload = MacroFlashUploadField(self.context, self.request, use_private=False, directly_upload=True, html_id=html_id)
        macro_flash_upload.field_name = self.name
        return macro_flash_upload.render() \
                 + '''<script src="%s" type="text/javascript"></script>''' % versionedURL('flash-upload.js')

class image_upload(FormInput):
    """ 表单选择字段 """

    def __init__(self, name, context, request, location, count=9,\
                 size_type=['original', 'compressed'],\
                 source_type=['album', 'camera'], **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request
        self.upload_url = location.absolute_url(self.request) + "/@@wechat_upload"
        self.field_name = name
        self.count = count
        self.size_type = size_type
        self.source_type= source_type
        self.items = []
        for i in self.value:
           img_obj = getUtility(IIntIds).queryObject(int(i))
           scr = img_obj.transformed_url(mime='image/x-thumbnail-png', subfile='image_tile')
           url = img_obj.transformed_url(mime='image/x-thumbnail-png', subfile='image_large')
           self.items.append({'intid':i, 'src': scr, 'url':url})

    html = ViewPageTemplateFile("templates/image_upload.pt")

class location(FormInput):
    """ 位置选择字段 """

    def __init__(self, name, context, request, return_type='wgs84', **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request
        self.return_type = return_type
        self.address = None
        # value
        # {
        #   "latitude":12, # 纬度，浮点数，范围为90 ~ -90
        #   'longitude':21, # 经度，浮点数，范围为180 ~ -180。
        #   'speed':12,   # 速度，以米/每秒计
        #   'accuracy':1,  # 位置精度
        #  }

        if self.value:
            if isinstance(self.value, basestring):
                self.value = json.loads(self.value)
            self.address = get_address(','.join(self.value['latitude'], self.value['longitude']))
        self.upload_url = self.context.absolute_url(self.request) + "/@@get_location"

    html = ViewPageTemplateFile("templates/location.pt")

class scanner(FormInput):
    """ 二维码、条码扫一扫 """

    def __init__(self, name, context, request,need_result=True, scan_type=["qrCode","barCode"], **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request
        self.need_result = 1 if need_result else 0
        self.scan_type = scan_type

    html = ViewPageTemplateFile("templates/scanner.pt")

class file_select(FormInput):
    """ 表单选择字段 """

    def __init__(self, name, context, request, multiple=False, **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request
        self.multiple = multiple

    def html(self):
        return FileSelectMacro(self.context, self.request,
                                          value=self.value,
                                          name=self.name,
                                          multiple=self.multiple,
                                          search_subtree=True,
                                          edit=True,
                                          upload=True).render()

class dataitem_select(FormInput):
    """ 表单选择字段 """

    def __init__(self, name, context, request, multiple=False, metadata='', **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request
        self.multiple = multiple
        self.metadata = metadata

    def html(self):
        return DataItemSelectMacro(self.context, self.request,
                                value=self.value, name=self.name,
                                multiple=self.multiple, metadata=self.metadata).render()

class datacontainer_select(FormInput):

    def __init__(self, name, context, request, multiple=False, metadata='', **kw):
        FormInput.__init__(self, name, **kw)
        self.context = context
        self.request = request
        self.multiple = multiple
        self.metadata = metadata

    def html(self):
        # 流程选择控件
        return FlowSelectMacro(self.context, self.request, \
                        value=self.value, name=self.name, \
                        multiple=self.multiple, metadata=self.metadata).render()


class image_paster(FormInput):

    def html(self):
        if not self.id:
            self.id = 'paster-%d' % random.randrange(0, 9999)
        attr = self._get_attr()
        data = self._get_data()
        return '''
            <div %s %s></div>
            <script type="text/javascript">
                load('paste_image.i18n.js', function() { new ImagePaster('%s', '#%s'); });
            </script>
        ''' % (attr, data, self.name, self.id)
