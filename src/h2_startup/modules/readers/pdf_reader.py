import fitz

from h2_startup.modules.readers.base_reader import BaseReader


class TextReader(BaseReader):
    # =============================================================================
    # user functions
    # =============================================================================
    def get_info(self, file_path: str) -> str | None:
        """Read all text from a pdf or docx file.

        Args:
            file_path (str): The path of the file.

        Returns:
            str: The extracted text from the file.
        """
        # instanciate string
        text = ""
        # page counter
        page_cmpt = 1
        # open pdf file
        document = fitz.open(file_path)

        # loop through pages
        for page in document:
            # retrieve text with start/end markers
            text += (
                f"<Page number {page_cmpt}>\n\n\n"
                + page.get_text()
                + f"\n\n\n</Page number {page_cmpt}>\n"
            )
            # update counter
            page_cmpt += 1

        # close file
        document.close()

        # remove trailing spaces and linebreaks
        text = text.rstrip("\n")
        text = text.strip()

        # return only if not empty
        if text:
            return text
        else:
            return None
