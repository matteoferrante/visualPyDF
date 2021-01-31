

class TextOutputFormatter:

    def __init__(self,resume,keywords=["abstract","introduction","methods and material","discussion","conclusion"]):
        self.resume=resume
        self.lower=resume.lower()
        self.keywords=keywords
        self.output=resume

    def prettify(self):
        """Looking for keywords in text, in particular abstract, return the start idx"""
        if "abstract" in self.lower:
            start_idx=self.lower.index("abstract")
            self.output=self.resume[start_idx:]
        return self.output