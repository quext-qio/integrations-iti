from jinja2 import BaseLoader, Environment

from qoops_logger import Logger

logging = Logger().instance("template mapper")


class TemplateMapper:
    """
    Class containing static methods for rendering and populating Jinja templates.
    """

    @staticmethod
    def render(template, values):
        """
        Renders a Jinja template with the provided values.

        Args:
            template (str): The Jinja template string.
            values (dict): Dictionary containing values to be inserted into the template.

        Returns:
            str: Rendered template data.
        """
        logging.info("Rendering the Template")
        template = Environment(loader=BaseLoader()).from_string(template)
        data = template.render(values)
        logging.info(f"Rendered Template: {data}")
        logging.info(f"Template Rendered - Returning data")
        return data

    @staticmethod
    def populate_jinja_values(template_values, template):
        """
        Populates Jinja values into a template.

        Args:
            template_values (dict): Dictionary containing values to be inserted into the template.
            template (str): The Jinja template string.

        Returns:
            str: Rendered template data with populated values.
        """
        logging.info("Populating Jinja Values")
        payload = TemplateMapper.render(template=template, values=template_values)
        logging.info("Populated Jinja Values - Returning payload")
        return payload
