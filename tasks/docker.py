"""Docker workflow tasks."""

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task

IMAGE_TAG = "template-dev-container"


def run_in_dev_container(c: Context, command: str) -> None:
    """Run a command in the development container.

    Args:
        c (Context): The Invoke context.
        command (str): The command to run.

    """
    c.run(
        f"devcontainer exec --workspace-folder . \
        --config .devcontainer/devcontainer.json \
        --mount-workspace-git-root true \
        --log-level debug {command}",
    )


@task
def build_docker(c: Context) -> None:
    """Build the Docker image and run the tests.

    This should be run from the Docker host.
    """
    c.run(f"docker build -t {IMAGE_TAG} .")


@task
def devcontainer_build(c: Context) -> None:
    """Build the development container."""
    c.run(
        f"devcontainer build \
            --image-name {IMAGE_TAG} \
            --label test-container={IMAGE_TAG} \
            --config .devcontainer/devcontainer.json \
            --workspace-folder . --log-level debug",
    )


@task
def devcontainer_up(c: Context) -> None:
    """Start the development container."""
    c.run("./scripts/dev-con-up.sh")


@task
def ci_docker(c: Context) -> None:
    """Run the tests in the Docker container."""
    build_docker(c)
    devcontainer_build(c)


@task
def exec_docker(c: Context) -> None:
    """Execute a shell in the Docker container."""
    result = c.run(
        'docker container ls --all --filter "label=dev.containers.project=loggy" --format "{{.ID}}"',
    )
    if result is not None:
        container_id = result.stdout.strip()
        if container_id:
            c.run(f"docker exec -it {container_id} /bin/bash", pty=True)
    else:
        print("No container found.")


docker_ns = Collection("docker")
docker_ns.add_task(build_docker, name="build")  # type: ignore[arg-type]
docker_ns.add_task(devcontainer_build, name="devcontainer_build")  # type: ignore[arg-type]
docker_ns.add_task(devcontainer_up, name="devcontainer_up")  # type: ignore[arg-type]
docker_ns.add_task(ci_docker, name="ci")  # type: ignore[arg-type]
docker_ns.add_task(exec_docker, name="exec")  # type: ignore[arg-type]
