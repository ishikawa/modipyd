from sphinx.builders.html import StandaloneHTMLBuilder


class OnlineHTMLBuilder(StandaloneHTMLBuilder):
    name = 'online'

    def init(self):
        # Add templates for online document
        self.config.templates_path.append('../../templates/online')
        super(OnlineHTMLBuilder, self).init()

