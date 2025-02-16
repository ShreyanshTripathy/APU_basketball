from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from .models import Team
from . import db


Teams = Blueprint('Teams', __name__)


@Teams.route('/add_team', methods=['GET', 'POST'])
@login_required
def add_new_team():
    # Check if the current user is authorized (admin with id=1)
    if current_user.id != 1:
        flash("You do not have permission to access this page.", category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        # Collect form data
        team_name = request.form.get('team_name')
        captain = request.form.get('captain')
        member_names = request.form.getlist('member_name[]')  # Handles dynamic fields


        # Validate input
        if not team_name or not captain or not member_names or any(not member for member in member_names):
            flash('Please fill out all fields!', 'error')
            return redirect(url_for('Teams.add_new_team'))
        else:

            try:

                # Create and save a new Event
                new_team = Team(
                    member_name = member_name,
                    team_name = team_name,
                    captain = captain,
                    admin_id=current_user.id  # Associate with the logged-in admin
                )
                db.session.add(new_team)
                db.session.commit()

                # Redirect to the home page with a success message
                flash('Team added successfully!', 'success')
                return redirect(url_for('Teams.view_teams'))

            except Exception as e:
                # Handle unexpected errors
                flash(f"An error occurred: {str(e)}", category='error')

    return render_template("add_team.html")

@Teams.route('/view_teams', methods=['GET'])
@login_required
def view_teams():
    # Fetch all teams from the database
    teams = Team.query.all()
    return render_template('view_teams.html', teams=teams)

@Teams.route('/edit_team/<int:team_id>', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    # Ensure the user is an admin
    if current_user.id != 1:
        flash("You do not have permission to access this page.", category='error')
        return redirect(url_for('Teams.view_teams'))

    # Fetch the team by ID
    team = Team.query.get_or_404(team_id)

    if request.method == 'POST':
        team_name = request.form.get('team_name')
        captain = request.form.get('captain')
        member_name = ','.join(request.form.getlist('member_name[]'))

        if not team_name or not captain or not member_name:
            flash('Please fill in all fields!', category='error')
        else:
            try:
                team.team_name = team_name
                team.captain = captain
                team.member_name = member_name
                db.session.commit()
                flash('Team updated successfully!', category='success')
                return redirect(url_for('Teams.view_teams'))
            except Exception as e:
                flash(f"An error occurred: {str(e)}", category='error')

    return render_template('edit_team.html', team=team)


@Teams.route('/delete_team/<int:team_id>', methods=['POST'])
@login_required
def delete_team(team_id):
    # Ensure the user is an admin
    if current_user.id != 1:
        flash("You do not have permission to access this action.", category='error')
        return redirect(url_for('Teams.view_teams'))

    team = Team.query.get_or_404(team_id)
    try:
        db.session.delete(team)
        db.session.commit()
        flash('Team deleted successfully!', category='success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}", category='error')

    return redirect(url_for('Teams.view_teams'))

