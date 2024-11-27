import sys
import jedi
from loguru import logger


class JdeiLib:
    def __init__(self, source, filename, project=None):
        self.filename = filename
        self.script = jedi.Script(source, path=filename, project=project)

    def getCallTips(self, line, index):
        """
        计算可能的调用提示的方法。

        @param params dictionary containing the method parameters
        @type dict
        """
        calltips = []

        try:
            signatures = self.script.get_signatures(line, index)
            for signature in signatures:
                name = signature.name
                params = self.extractParameters(signature)
                calltips.append("{0}{1}".format(name, params))
        except Exception as err:
            logger.error(str(err))

        return calltips

    def extractParameters(self, signature):
        """
        用于提取调用参数描述的方法。

        @param signature a jedi signature object
        @type object
        @return a string with comma seperated parameter names and default
            values
        @rtype str
        """
        try:
            params = ", ".join(
                [param.description.split("param ", 1)[-1] for param in signature.params]
            )
            return "({0})".format(params)
        except AttributeError:
            # Empty strings as argspec suppress display of "definition"
            return " "

    def getDocumentation(self, line, index):
        """
        获取一些源代码文档的方法。

        @param params dictionary containing the method parameters
        @type dict
        """

        docu = {}

        try:
            definitions = self.script.infer(line, index)
            definition = definitions[0]  # use the first one only
            docu = {
                "name": definition.full_name,
                "module": definition.module_name,
                "argspec": self.extractParameters(definition),
                "docstring": definition.docstring(),
            }
        except Exception as err:
            logger.error(str(err))
        return docu

    def getHoverHelp(self, line, index):
        """
        获取一些源代码文档的方法。

        @param params dictionary containing the method parameters
        @type dict
        """
        try:
            helpText = self.script.help(line, index)[0].docstring()
            return helpText
        except Exception as err:
            logger.error(str(err))

    def getAssignment(self, line, index):
        """
        获取参数定义位置的方法。

        @param params dictionary containing the method parameters
        @type dict
        """
        gotoDefinition = {}
        flag_path = self.filename
        if sys.platform == "win32":
            flag_path = flag_path.replace("/", "\\")
        try:
            assignments = self.script.goto(
                line, index, follow_imports=True, follow_builtin_imports=True
            )
            for assignment in assignments:
                if bool(assignment.module_path):
                    gotoDefinition = {
                        "ModulePath": str(assignment.module_path),
                        "Line": (0 if assignment.line is None else assignment.line),
                        "Column": assignment.column,
                    }
                    if (
                            gotoDefinition["ModulePath"] == flag_path
                            and gotoDefinition["Line"] == line
                    ):
                        return
                break
        except Exception as err:
            logger.error(str(err))

        return gotoDefinition

    def getReferences(self, line, index, ):
        """
        获取引用参数的位置的方法。

        @param params dictionary containing the method parameters
        @type dict
        """
        gotoReferences = []
        flag_path = self.filename
        if sys.platform == "win32":
            flag_path = flag_path.replace("/", "\\")
        try:
            references = self.script.get_references(line, index, include_builtins=False)
            for reference in references:
                if bool(reference.module_path):
                    if (
                            reference.line == line
                            and str(reference.module_path) == flag_path
                    ):
                        continue
                    gotoReferences.append(
                        {
                            "ModulePath": str(reference.module_path),
                            "Line": (0 if reference.line is None else reference.line),
                            "Column": reference.column,
                            "Code": reference.get_line_code(),
                        }
                    )
        except Exception as err:
            logger.error(str(err))

        return gotoReferences

    def get_syntax_errors(self):
        ret = []
        syntax_info = self.script.get_syntax_errors()
        for syntax_error in syntax_info:
            ret.append(dict(line=syntax_error.line,
                            start_column=syntax_error.column,
                            end_column=syntax_error.until_column,
                            error_info=syntax_error.get_message()
                            ))
        return ret

    def __completionFullName(self, completion):
        """
        Private method to extract the full completion name.

        @param completion reference to the completion object
        @type jedi.api.classes.Completion
        @return full completion name
        @rtype str
        """
        fullName = completion.full_name
        fullName = (
            fullName.replace("__main__", completion.module_name)
            if fullName
            else completion.module_name
        )

        return fullName

    def __completionType(self, completion):
        """
        Private method to assemble the completion type depending on the
        visibility indicated by the completion name.

        @param completion reference to the completion object
        @type jedi.api.classes.Completion
        @return modified completion type
        @rtype str
        """
        if completion.name.startswith("__"):
            compType = "__" + completion.type
        elif completion.name.startswith("_"):
            compType = "_" + completion.type
        else:
            compType = completion.type

        return compType

    def getCompletions(self, line, index):
        """
        用于计算可能完成的公共方法。

        @param params dictionary containing the method parameters
        @type dict
        """
        response = []

        try:
            completions = self.script.complete(line, index, fuzzy=False)
            for completion in completions:
                if not (completion.name.startswith("__")
                        and completion.name.endswith("__")):
                    response.append({
                        'label': completion.name,
                        'kind': self.__completionType(completion),
                        'insertText': completion.name,
                        'detail': self.__completionFullName(completion),
                        'documentation': None
                    })
        except Exception as e:
            logger.error(str(e))

        return response
