import { parametrize } from 'react-overridable';
import { ResourceTypeField } from "@js/invenio_rdm_records";

// Allow form to show up, but disable modification
// default value set inside of invenio.cfg APP_RDM_DEPOSIT_FORM_DEFAULTS setting
export const CustomResourceTypeField = parametrize(ResourceTypeField, {
  label: "Application Resource Type",
  disabled: true
});