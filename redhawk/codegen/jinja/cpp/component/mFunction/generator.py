from redhawk.codegen.jinja.cpp.component.pull.generator import PullComponentGenerator
from redhawk.codegen.jinja.common import ShellTemplate, AutomakeTemplate, AutoconfTemplate
from redhawk.codegen.jinja.loader import CodegenLoader
from redhawk.codegen.jinja.template import TemplateFile
from redhawk.codegen.jinja.cpp import CppTemplate
from mapping import MFunctionMapper

if not '__package__' in locals():
    # Python 2.4 compatibility
    __package__ = __name__.rsplit('.', 1)[0]

loader = CodegenLoader(__package__,
                       {'pull'       : 'redhawk.codegen.jinja.cpp.component.pull',
                        'mFunction'  : 'redhawk.codegen.jinja.cpp.component.mFunction',
                        'common'     : 'redhawk.codegen.jinja.common',
                        'properties' : 'redhawk.codegen.jinja.cpp.properties',
                        'base'       : 'redhawk.codegen.jinja.cpp.component.base'})

class OctaveComponentGenerator(PullComponentGenerator):
    '''
    A generator that is very similar to the C++ pull generator.  This generator 
    differs form its parent in 4 primary regards:

        1. The octaveResource.cpp/octaveResource_base.cpp/octaveResource.h/
           octaveResource_base.h are used in alternative to resource.cpp/
           resource_base.cpp/resource.h/resource_base.h.  A custom main.cpp
           is also used.

        2. The COPYING template is included (this template contains GPL info).

        3. A list of varargin arguments is created and sorted.  This pertains
           to mFunctions with variable numbers of input arguments.

        4. The mFunction mapper is referenced instead of the pull mapper.

    '''

    def templates(self, component):
        templates = [
            CppTemplate('mFunction/main.cpp'),
            AutomakeTemplate('base/Makefile.am'),
            AutomakeTemplate('base/Makefile.am.ide',
                             userfile=True),
            AutoconfTemplate('configure.ac'),
            ShellTemplate('base/build.sh'),
            ShellTemplate('common/reconf'),
            CppTemplate('octaveResource_base.cpp',
                        component['baseclass']['file']),
            CppTemplate('octaveResource_base.h',
                        component['baseclass']['header']),
            CppTemplate('octaveResource.cpp',
                        component['userclass']['file'],
                        userfile=True),
            CppTemplate('octaveResource.h',
                        component['userclass']['header'],
                        userfile=True),
            TemplateFile('COPYING')
        ]

        # Add port implementations if required
        templates.extend(CppTemplate('pull/'+fn) for fn in self.getPortTemplates(component))

        if component['structdefs']:
            templates.append(CppTemplate('pull/struct_props.h'))

        return templates

    def loader(self, component):
        return loader

    def map(self, softpkg):
        component = PullComponentGenerator.map(self, softpkg)

        # Create a list of varargin inputs.  varargin inputs can be either
        # ports of properties.  Having a list allows us to sort a list
        # of varargin ports and properties by name, which allows us to
        # order the arguments correctly when passing them to the feval call
        # in the code template.
        component['vararginList'] = []

        if component.has_key('properties'):
            for property in component['properties']:
                if property['cppname'].find("varargin") == 0:
                    component['vararginList'].append(property['cppname'])
        if component.has_key('ports'):
            for port in component['ports']:
                if port['cppname'].find("varargin") == 0:
                    component['vararginList'].append(port['cppname'])
        component['vararginList'].sort()

        return component

    def componentMapper(self):
        return MFunctionMapper()
