class element_has_attribute(object):
    """An expectation for checking that an element has a particular css class.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(
            *self.locator)   # Finding the referenced element
        if element.get_attribute("style") == '' \
                or element.get_attribute("style") == 'display: none;':
            return element
        else:
            return False
