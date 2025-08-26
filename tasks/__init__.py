"""Invoke tasks for managing the project."""

from invoke.collection import Collection

import tasks.github_actions as act
from tasks import ci, docker, docs, git, pre_commit, python, release

namespace = Collection()
namespace.add_collection(ci.ci_ns)
namespace.add_collection(docs.doc_ns)
namespace.add_collection(python.python_ns)
namespace.add_collection(docker.docker_ns)
namespace.add_collection(pre_commit.pre_commit_ns)
namespace.add_collection(release.release_ns)
namespace.add_collection(act.act_ns)
namespace.add_collection(git.git_ns)
