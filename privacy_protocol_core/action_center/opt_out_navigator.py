# Placeholder for helping users navigate opt-out processes
class OptOutNavigator:
    def __init__(self):
        # This could be populated from a database or configuration file
        self.opt_out_links = {
            "example_service.com": "https://example_service.com/privacy/opt-out",
            "another_service.net": "https://another_service.net/settings/privacy"
        }
        self.deletion_templates = {
            "default": "Dear [Service Name],\n\nPlease delete my account and all associated personal data as per my rights under [applicable regulation, e.g., GDPR, CCPA].\n\nMy account details are:\n[Username/Email]\n\nThank you,\n[Your Name]"
        }

    def get_opt_out_link(self, service_url_or_name):
        """Provides a direct link to the opt-out page if known."""
        for key, link in self.opt_out_links.items():
            if key in service_url_or_name:
                return link
        return None

    def get_data_deletion_template(self, service_name, user_name, user_contact, regulation="GDPR/CCPA"):
        """Provides a pre-filled email template for data deletion requests."""
        template = self.deletion_templates.get("default", "")
        return template.replace("[Service Name]", service_name)\
                       .replace("[applicable regulation, e.g., GDPR, CCPA]", regulation)\
                       .replace("[Username/Email]", user_contact)\
                       .replace("[Your Name]", user_name)
