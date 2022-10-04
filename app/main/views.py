#!usr/bin/env python
# -*- coding:utf-8 _*-
# Create by hex7 at 11/22/18
#

from datetime import datetime
from platform import platform
from flask import render_template, session, redirect, url_for, flash, abort
from flask import request, current_app, make_response, jsonify
from flask_paginate import Pagination
# from flask_login import login_required
# from flask_login import current_user
from . import main
# from .forms import NameForm, EditProfileForm, EditProfileAdminForm
# from .forms import PostForm, CommentForm
from .. import db
from ..models import TRTFailedRecord
# from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    
#     form = PostForm()
#     if current_user.can(Permission.WRITE) and form.validate_on_submit():
#         post = Post(body=form.body.data,
#                     author=current_user._get_current_object())
#         db.session.add(post)
#         db.session.commit()
#         return redirect(url_for('.index'))
#     # posts = Post.query.order_by(Post.timestamp.desc()).all()
#     page = request.args.get('page', 1, type=int)
#     show_followed = False
#     if current_user.is_authenticated:
#         show_followed = bool(request.cookies.get('show_followed', ''))
#     if show_followed:
#         query = current_user.followed_posts
#     else:
#         query = Post.query
#     print(current_app.config)
#     per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
#     pagination = query.order_by(Post.timestamp.desc()).paginate(
#         page, per_page=per_page,
#         error_out=False)
#     posts = pagination.items
    trt_list = []
    cuda_list = []
    os_list = []
    arch_list = []
    case_list = []
    category_list = []
    gpu_list = []

    query = TRTFailedRecord.query
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORD_PER_PAGE']
    data = query.order_by(TRTFailedRecord.id.asc()).paginate(
        page, per_page=per_page,
        error_out=False)
    pagination = Pagination(page=page, total=0)

    version_list = get_versions()

    if version_list:
        current_version = version_list[0]
        data = query.filter_by(version=current_version).order_by(TRTFailedRecord.id.asc()).paginate(
            page, per_page=per_page,
            error_out=False)

        count = query.filter_by(version=current_version).count()
        pagination = Pagination(page=page, per_page=per_page, total=count)

        result = get_version_data(current_version)

        trt_list = result['trt'] 
        arch_list = result['arch'] 
        cuda_list = result['cuda'] 
        gpu_list = result['gpu'] 
        os_list = result['os'] 
        category_list = result['category'] 
        case_list = result['cases'] 

    data = data.items

    return render_template('index.html', data=data, version_list=version_list, trt_list=trt_list, 
        cuda_list=cuda_list, gpu_list=gpu_list, os_list=os_list, 
        arch_list=arch_list, category_list=category_list, case_list=case_list, pagination=pagination)


@main.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        id = request.form['id']
        category = request.form['category']
        nvbug = request.form['nvbug']

        TRTFailedRecord.update_case(id, category, nvbug)

        print(id)

    return jsonify('save ok.')

@main.route('/change_version', methods=['GET', 'POST'])
def change_version():
    if request.method == 'POST':
        version = request.form['version']
        output = get_version_data(version) 

    return jsonify(output)

@main.route('/change_filter', methods=['GET', 'POST'])
def change_filter():
    if request.method == 'POST':
        version = request.form['version']
        trt = request.form['trt']
        cuda = request.form['cuda']
        gpu = request.form['gpu']
        os = request.form['os']

        output = get_filter_data(version, trt, cuda, gpu, os) 

    return jsonify(output)

@main.route('/load_data', methods=['GET', 'POST'])
def load_data():

    version = get_versions()[0]
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['RECORD_PER_PAGE']
    if request.method == 'POST':
        version = request.form['version']
        trt = request.form['trt']
        cuda = request.form['cuda']
        os = request.form['os']
        arch = request.form['arch']
        category = request.form['category']
        case_name = request.form['case_name']
        gpu = request.form['gpu']

        data, count = get_data(page, per_page, version, trt, cuda, gpu, os, arch, category, case_name)

        pagination = Pagination(page=page, per_page=per_page, total=count)

        output = {
                    'recordhtml': render_template('record.html', data=data.items),
                    'pagehtml': render_template('page.html', pagination=pagination)
                }

        return jsonify(output)
    else:
        data, count = get_data(page, per_page, version)
        pagination = Pagination(page=page, per_page=per_page, total=count)

        return 'msg'


# @main.route('/user/<username>', methods=['GET', 'POST'])
# def user(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     if user is None:
#         abort(404)
#     # posts = user.posts.order_by(Post.timestamp.desc()).all()
#     per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
#     page = request.args.get('page', 1, type=int)
#     pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
#         page, per_page=per_page,
#         error_out=False)
#     posts = pagination.items
#     return render_template('user.html', user=user, posts=posts,
#                            pagination=pagination)


# @main.route('/edit-profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#     form = EditProfileForm()
#     if form.validate_on_submit():
#         current_user.name = form.name.data
#         current_user.location = form.location.data
#         current_user.about_me = form.about_me.data
#         db.session.add(current_user._get_current_object())
#         db.session.commit()
#         flash('Your profile has been updated.')
#         return redirect(url_for('.user', username=current_user.username))

#     form.name.data = current_user.name
#     form.location.data = current_user.location
#     form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', form=form)


# @main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def edit_profile_admin(id):
#     user = User.query.get_or_404(id)
#     form = EditProfileAdminForm(user=user)
#     if form.validate_on_submit():
#         user.email = form.email.data
#         user.username = form.username.data
#         user.confirmed = form.confirmed.data
#         user.role = Role.query.get(form.role.data)
#         user.name = form.name.data
#         user.location = form.location.data
#         user.about_me = form.about_me.data
#         db.session.add(user)
#         db.session.commit()
#         flash('The profile has been updated.')
#         return redirect(url_for('.user', username=user.username))

#     form.email.data = user.email
#     form.username.data = user.username
#     form.confirmed.data = user.confirmed
#     form.role.data = user.role_id
#     form.name.data = user.name
#     form.location.data = user.location
#     form.about_me.data = user.about_me
#     return render_template('edit_profile.html', form=form, user=user)


# @main.route('/post/<int:id>', methods=['GET', 'POST'])
# def post(id):
#     post = Post.query.get_or_404(id)
#     form = CommentForm()
#     if form.validate_on_submit():
#         comment = Comment(body=form.body.data, post=post,
#                           author=current_user._get_current_object())
#         db.session.add(comment)
#         db.session.commit()
#         flash('Your comment has been published.')
#         return redirect(url_for('.post', id=post.id, page=-1))
#     page = request.args.get('page', 1, type=int)
#     if page == -1:
#         # go to last page
#         page = (post.comments.count() - 1) // \
#                 current_app.config['FLASK_COMMENTS_PER_PAGE'] + 1
#     pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
#         page, per_page=current_app.config['FLASK_COMMENTS_PER_PAGE'],
#         error_out=False)
#     comments = pagination.items
#     return render_template('post.html', posts=[post], form=form,
#                            comments=comments, pagination=pagination)


# @main.route('/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit(id):
#     post = Post.query.get_or_404(id)
#     if current_user != post.author and \
#             not current_user.can(Permission.ADMIN):
#         abort(403)
#     form = PostForm()
#     if form.validate_on_submit():
#         post.body = form.body.data
#         db.session.add(post)
#         db.session.commit()
#         flash('The post has been updated.')
#         return redirect(url_for('.post', id=post.id))

#     form.body.data = post.body
#     return render_template('edit_post.html', form=form)


# @main.route('/all')
# @login_required
# def show_all():
#     resp = make_response(redirect(url_for('.index')))
#     resp.set_cookie('show_followed', '', max_age=30*24*60*60)
#     return resp


def get_version_data(version):
    
    trt_list = get_trt(version)
    cuda_list = get_cuda(version)
    gpu_list = get_gpu(version)
    os_list = get_os(version)
    arch_list = get_arch(version)
    category_list = get_category(version)
    case_list = get_cases(version)
    
    output = {
        'trt': trt_list, 
        'cuda': cuda_list, 
        'gpu': gpu_list,
        'os': os_list,
        'arch': arch_list,
        'category': category_list,
        'cases': case_list
    }

    return output

def get_filter_data(version, trt, cuda, gpu, os):
    
    trt_list = get_trt(version)
    cuda_list = get_cuda(version, trt)
    gpu_list = get_gpu(version, trt, cuda)
    os_list = get_os(version, trt, cuda)
    arch_list = get_arch(version, trt, os)
    category_list = get_category(version)
    case_list = get_cases(version, trt, cuda, gpu)
    
    output = {
        'trt': trt_list, 
        'cuda': cuda_list, 
        'gpu': gpu_list,
        'os': os_list,
        'arch': arch_list,
        'category': category_list,
        'cases': case_list
    }

    return output

def get_versions():
    result = TRTFailedRecord.query.distinct(
                TRTFailedRecord.version).order_by(TRTFailedRecord.version.desc())

    output = [item.version for item in result]

    return output

def get_trt(version):
    result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.trt).filter_by(
                version=version).order_by(TRTFailedRecord.trt.desc())

    output = [item.trt for item in result]

    return output 
    
def get_cuda(version, trt=''):
    if len(trt) == 0:
        result = TRTFailedRecord.query.distinct(
                TRTFailedRecord.cuda).filter_by(
                    version=version).order_by(TRTFailedRecord.cuda.desc())
    else:
        result = TRTFailedRecord.query.distinct(
                TRTFailedRecord.cuda).filter_by(
                    version=version, trt=trt).order_by(TRTFailedRecord.cuda.desc())

    output = [item.cuda for item in result]

    return output
    
def get_gpu(version, trt='', cuda=''):
    if len(trt) == 0 and len(cuda) == 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.platform).filter_by(
                        version=version).order_by(TRTFailedRecord.platform.desc())
    elif len(cuda) == 0 and len(trt) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.platform).filter_by(
                        version=version, trt=trt).order_by(TRTFailedRecord.platform.desc())
    elif len(trt) == 0 and len(cuda) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.platform).filter_by(
                        version=version, cuda=cuda).order_by(TRTFailedRecord.platform.desc())
    else:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.platform).filter_by(
                        version=version, trt=trt, cuda=cuda).order_by(TRTFailedRecord.platform.desc())

    output = [item.platform for item in result]

    return output

def get_os(version, trt='', cuda=''):
    if len(trt) == 0 and len(cuda) == 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.os).filter_by(
                        version=version)
    elif len(cuda) == 0 and len(trt) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.os).filter_by(version=version, trt=trt)
    elif len(trt) == 0 and len(cuda) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.os).filter_by(version=version, cuda=cuda)
    else:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.os).filter_by(version=version, trt=trt, cuda=cuda)

    output = [item.os for item in result]

    return output

def get_arch(version, trt='', os=''):
    if len(trt) == 0 and len(os) == 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.arch).filter_by(
                        version=version)
    elif len(os) == 0 and len(trt) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.arch).filter_by(version=version, trt=trt)
    elif len(trt) == 0 and len(os) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.arch).filter_by(version=version, os=os)
    else:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.arch).filter_by(version=version, trt=trt, os=os)

    output = [item.arch for item in result]

    return output

def get_cases(version, trt='', cuda='', gpu=''):
    if len(trt) == 0 and len(cuda) == 0 and len(gpu) == 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.case_name).filter_by(
                        version=version)
    elif len(cuda) == 0 and len(gpu) == 0 and len(trt) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.case_name).filter_by(version=version, trt=trt)
    elif len(trt) == 0 and len(gpu) == 0 and len(cuda) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.case_name).filter_by(version=version, cuda=cuda)
    elif len(trt) == 0 and len(cuda) == 0 and len(gpu) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.case_name).filter_by(version=version, platform=gpu)
    elif len(trt) == 0 and len(cuda) != 0 and len(gpu) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.case_name).filter_by(version=version, cuda=cuda, platform=gpu)
    elif len(cuda) == 0 and len(trt) != 0 and len(gpu) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.case_name).filter_by(version=version, trt=trt, platform=gpu)
    elif len(gpu) == 0 and len(trt) != 0 and len(cuda) != 0:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.case_name).filter_by(version=version, trt=trt, cuda=cuda)
    else:
        result = TRTFailedRecord.query.distinct(
                    TRTFailedRecord.arch).filter_by(version=version, trt=trt, cuda=cuda, platform=gpu)

    output = [item.case_name for item in result]

    return output


def get_category(version):
    result = TRTFailedRecord.query.distinct(
        TRTFailedRecord.category).filter_by(
            version=version)

    output = [item.category for item in result]

    return output


def get_data(page, per_page, version, trt='', cuda='', gpu='', os='', arch='', category='', case_name=''):

    if len(trt) == 0:
        trt_list = get_trt(version=version)
    else:
        trt_list = [trt]

    if len(cuda) == 0:
        cuda_list = get_cuda(version=version, trt=trt)
    else:
        cuda_list = [cuda]
    
    if len(gpu) == 0:
        gpu_list = get_gpu(version=version, trt=trt, cuda=cuda)
    else:
        gpu_list = [gpu]
    
    if len(os) == 0:
        os_list = get_os(version=version, trt=trt, cuda=cuda)
    else:
        os_list = [os]
    
    if len(arch) == 0:
        arch_list = get_arch(version=version, trt=trt, os=os)
    else:
        arch_list = [arch]

    if len(category) == 0:
        category_list = get_category(version=version)
    else:
        category_list = [category]

    if len(case_name) == 0:
        case_list = get_cases(version=version, trt=trt, cuda=cuda, gpu=gpu)
    else:
        case_list = [case_name]

    query = TRTFailedRecord.query
    
    data = query.filter(
        TRTFailedRecord.trt.in_(trt_list), 
        TRTFailedRecord.platform.in_(gpu_list), 
        TRTFailedRecord.os.in_(os_list), 
        TRTFailedRecord.arch.in_(arch_list), 
        TRTFailedRecord.category.in_(category_list), 
        TRTFailedRecord.case_name.in_(case_list), 
        TRTFailedRecord.cuda.in_(cuda_list)).order_by(TRTFailedRecord.id.asc()).paginate(
            page, per_page=per_page,
            error_out=False)

    count = query.filter(TRTFailedRecord.trt.in_(trt_list), 
        TRTFailedRecord.platform.in_(gpu_list), 
        TRTFailedRecord.os.in_(os_list), 
        TRTFailedRecord.arch.in_(arch_list), 
        TRTFailedRecord.category.in_(category_list), 
        TRTFailedRecord.case_name.in_(case_list), 
        TRTFailedRecord.cuda.in_(cuda_list)).count()

    return data, count
