from collections import defaultdict


class GroupDependencies:
    """represents the dependencies for a group of groups
    held internally as a dict(string,set) where set contains dependent ids
    set used to prevent duplicates

    To add a dependency either call add with a single dependency
    or update with another dependency object

    To access dependencies for a question id simply index
    i.e  a['question_id']
    indexing is read only
    """

    def __init__(self):
        self._group_dependencies = defaultdict(set)
        self._group_dependencies['group_drivers'] = set()
        self._group_dependencies['block_drivers'] = set()

    def __len__(self):
        """
        returns length of group dependencies, needed for index access
        -2 refers to the group and block drivers
        """

        return len(self._group_dependencies) - 2

    def __getitem__(self, group_id):
        """allows the support of indexing e.g a[group_id]"""
        return self._group_dependencies[group_id]

    @property
    def group_dependencies(self):
        return self._group_dependencies

    def add(self, dependent_id, dependency_driver_id, group_or_block):
        """ Adds a dependency to a specific group_id """
        self._group_dependencies[dependent_id].add(dependency_driver_id)
        if group_or_block == 'block':
            self._group_dependencies['block_drivers'].add(dependency_driver_id)
        if group_or_block == 'group':
            self._group_dependencies['group_drivers'].add(dependency_driver_id)

    def update(self, other):
        for key, dependencies in other.group_dependencies.items():
            self.group_dependencies[key] |= dependencies


def get_group_dependencies(schema):
    """
    gets the all the answer dependencies for a schema by walking through repeats
    """
    dependencies = GroupDependencies()

    for group in schema.groups:
        if group.get('routing_rules') and not _group_has_relationship_type(schema, group['blocks']):
            for routing_rule in group['routing_rules']:
                if _routing_rule_has_repeat(routing_rule):
                    if 'group_ids' in routing_rule['repeat']:
                        dependencies.update(
                            get_dependency_drivers_from_group_ids(group['id'],
                                                                  routing_rule['repeat']['group_ids']))
                    else:
                        dependencies.update(
                            get_dependency_driver_from_answer_id(schema,
                                                                 group['id'],
                                                                 routing_rule['repeat']['answer_id']))

    return dependencies


def get_dependency_drivers_from_group_ids(dependent_group_id, group_ids):
    dependencies = GroupDependencies()
    for group_id in group_ids:
        dependencies.add(dependent_group_id, group_id, 'group')

    return dependencies


def get_dependency_driver_from_answer_id(schema, dependent_group_id, answer_id):
    dependencies = GroupDependencies()
    question_id = schema.get_answer(answer_id)['parent_id']
    block_id = schema.get_question(question_id)['parent_id']
    dependencies.add(dependent_group_id, block_id, 'block')

    return dependencies


def _group_has_relationship_type(schema, blocks):
    for block in blocks:
        if schema.is_block_relationship_type(block['id']):
            return True

    return False


def _routing_rule_has_repeat(routing_rule):
    dependent_routing_types = ['group', 'answer_count', 'answer_count_minus_one']
    if routing_rule.get('repeat') and routing_rule['repeat'].get('type') in dependent_routing_types:
        return True
    return False
