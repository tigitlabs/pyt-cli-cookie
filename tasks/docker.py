"""Docker workflow tasks."""

import json
import pprint

from invoke.collection import Collection
from invoke.context import Context
from invoke.runners import Result
from invoke.tasks import task

from tasks.git import GitFlow


class Docker:
    """Docker workflow tasks."""

    def __init__(self, c: Context) -> None:
        """Initialize the Docker class.

        Args:
            c (Context): The Invoke context.
        """
        self.c = c
        self.project_name = GitFlow(c).get_repo_name()
        self.image_name = self.project_name
        self.container_name = self.project_name
        self.tag = "dev"

    def build(self, tag: str) -> None:
        """Build the Docker image.

        Args:
            tag (str): The image tag.
        """
        self.c.run(f"docker build --build-arg PROJECT_NAME={self.project_name} -t {self.image_name}:{self.tag} .")

    def inspect_image(self) -> dict:
        """Inspect the Docker image."""
        cmd = f"docker image inspect {self.image_name}:{self.tag} --format '{{{{json .Config.Labels}}}}'"
        result = self.c.run(cmd, hide=True)
        meta = json.loads(result.stdout)  # type: ignore
        print("Image metadata:")
        pprint.pprint(meta)
        return meta

    def run(self, command: str) -> Result:
        """Run a command in the Docker container."""
        cmd = f"docker run --rm -i {self.image_name}:{self.tag} {command}"
        r = self.c.run(cmd, hide=True, warn=True)
        if r is None:
            raise RuntimeError("Docker run command failed with no result.")
        return r

    def check_package(self, package: str) -> None:
        """Check the version of a package in the Docker container."""
        r = self.run(f"{package} --version")
        version = r.stdout.strip()
        if version is None or version == "":
            raise RuntimeError(f"Failed to get version for package {package}.")
        print(f"✅ {package} version: {r.stdout.strip()}")

    def shell(self) -> None:
        """Run the container and start a shell session ."""
        cmd = f"docker run --rm -it {self.image_name}:{self.tag} /bin/bash"
        result = self.c.run(cmd, pty=True)
        if result is not None:
            print(result)
        else:
            print("Run command failed.")

    def exec_docker(self) -> None:
        """Execute a shell in the Docker container."""
        cmd = (
            "docker container ls --all "
            f'--filter "label=dev.containers.project={self.project_name}" '
            '--format "{{.ID}}"'
        )
        print(cmd)
        result = self.c.run(cmd)
        if result is not None:
            print(result)
            container_id = result.stdout.strip()
            if container_id:
                self.c.run(f"docker exec -it {container_id} /bin/bash", pty=True)
        else:
            print("No container found.")


class DevContainer:
    """Class to manage development container operations."""

    def __init__(self, c: Context) -> None:
        """Initialize the DevContainer class.

        Args:
            c (Context): The Invoke context.
        """
        self.c = c
        self.image_name = GitFlow(c).get_repo_name()
        self.project_name = self.image_name
        self.tag = "dev"
        self.id_label = f"dev.containers.project={self.project_name}"

    def build(self) -> None:
        """Build the development container."""
        self.c.run(
            f"devcontainer build \
                --image-name dev-cont-{self.image_name}:{self.tag} \
                --label {self.id_label} \
                --config .devcontainer/devcontainer.json \
                --workspace-folder . --log-level debug",
        )

    def up(self, remove_existing: bool = False) -> None:
        """Start the development container."""
        cmd = (
            "devcontainer up "
            "--workspace-folder . "
            "--config .devcontainer/devcontainer.json "
            f"--id-label {self.id_label}:{self.tag} "
            "--log-level debug "
        )
        if remove_existing:
            cmd += "--remove-existing-container"
        print(cmd)
        self.c.run(cmd)

    def run(self, command: str) -> None:
        """Run a command in the development container.

        Args:
            command (str): The command to run.
        """
        self.up()
        self.run_in_dev_container(command)

    def run_in_dev_container(self, command: str) -> None:
        """Run a command in the development container.

        Args:
            command (str): The command to run.

        """
        cmd = (
            f"devcontainer exec --workspace-folder . "
            "--config .devcontainer/devcontainer.json "
            "--mount-workspace-git-root true "
            f"--id-label {self.id_label}:{self.tag} "
            f"--log-level debug {command} "
        )
        print(cmd)
        self.c.run(cmd, pty=True)


@task
def test_devcontainer(c: Context) -> None:
    """Run the tests in the container."""
    DevContainer(c).run("poetry install")
    DevContainer(c).run("poetry run pytest")


@task
def build_docker(c: Context) -> None:
    """Build the Docker image and run the tests.

    This should be run from the Docker host.
    """
    Docker(c).build(tag="dev")


@task
def devcontainer_build(c: Context) -> None:
    """Build the development container."""
    DevContainer(c).build()


@task(pre=[build_docker])
def test_docker(c: Context) -> None:
    """Run the tests in the Docker container."""
    Docker(c).check_package("poetry")
    Docker(c).check_package("pyenv")


@task()
def shell_docker(c: Context) -> None:
    """Execute a shell in the Docker container."""
    Docker(c).shell()


@task
def inspect_image(c: Context) -> None:
    """Inspect the Docker image."""
    Docker(c).inspect_image()


@task
def ci_docker(c: Context) -> None:
    """Run the tests in the Docker container."""
    build_docker(c)
    test_docker(c)
    devcontainer_build(c)
    test_devcontainer(c)


@task
def exec_docker(c: Context) -> None:
    """Execute a shell in the Docker container."""
    Docker(c).exec_docker()


docker_ns = Collection("docker")
docker_ns.add_task(build_docker, name="build")  # type: ignore[arg-type]
docker_ns.add_task(inspect_image, name="inspect")  # type: ignore[arg-type]
docker_ns.add_task(test_docker, name="test")  # type: ignore[arg-type]
docker_ns.add_task(shell_docker, name="shell")  # type: ignore[arg-type]
docker_ns.add_task(test_devcontainer, name="devcontainer_test")  # type: ignore[arg-type]
docker_ns.add_task(devcontainer_build, name="devcontainer_build")  # type: ignore[arg-type]
docker_ns.add_task(ci_docker, name="ci")  # type: ignore[arg-type]
docker_ns.add_task(exec_docker, name="exec")  # type: ignore[arg-type]
